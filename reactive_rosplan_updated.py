#!/usr/bin/env python3

import time
import rospy
import subprocess
import os
import signal

from std_srvs.srv import Empty
from rosplan_dispatch_msgs.srv import GetPlanService
from rosplan_dispatch_msgs.msg import ActionDispatch
from rosplan_knowledge_msgs.srv import GetAttributeService

def call_rosplan_services():
    rospy.wait_for_service("/rosplan_problem_interface/problem_generation_server")
    rospy.wait_for_service("/rosplan_planner_interface/planning_server")

    try:
        generate_problem = rospy.ServiceProxy("/rosplan_problem_interface/problem_generation_server", Empty)
        plan = rospy.ServiceProxy("/rosplan_planner_interface/planning_server", Empty)

        print("Calling problem generation...")
        generate_problem()
        time.sleep(2)

        print("Calling planner...")
        plan()
        time.sleep(2)

    except rospy.ServiceException as e:
        print(f"Service call failed: {e}")

def get_plan():
    rospy.wait_for_service("/rosplan_parsing_interface/get_plan")
    get_plan_srv = rospy.ServiceProxy("/rosplan_parsing_interface/get_plan", GetPlanService)
    return get_plan_srv().plan

def check_task_failed():
    rospy.wait_for_service("/rosplan_knowledge_base/state/propositions")
    get_props = rospy.ServiceProxy("/rosplan_knowledge_base/state/propositions", GetAttributeService)
    result = get_props("task_failed")
    for prop in result.attributes:
        if prop.attribute_name == "task_failed" and not prop.is_negative:
            return True
    return False

def dispatch_plan_step_by_step(plan):
    pub = rospy.Publisher("/action_dispatch", ActionDispatch, queue_size=10)
    rospy.sleep(1.0)

    for action in plan:
        rospy.loginfo(f"Dispatching action: {action.name} with parameters: {[p.value for p in action.parameters]}")
        pub.publish(action)
        rospy.sleep(3.0)  # Allow time for action execution

        if check_task_failed():
            print("⚠️ task_failed is True. Stopping execution.")
            break

def main_gui(domain_path, instance_path):
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    
    rospy.init_node("reactive_rosplan", anonymous=True)

    call_rosplan_services()

    plan = get_plan()
    if not plan:
        print("No plan found.")
        return []

    dispatch_plan_step_by_step(plan)

    return [f"{a.name}({', '.join([p.value for p in a.parameters])})" for a in plan]

