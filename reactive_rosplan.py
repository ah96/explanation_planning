#!/usr/bin/env python3

import time
import rospy
from std_srvs.srv import Empty
import subprocess
import os
#from rosplan_dispatch_msgs.srv import GetPlanService
#from rosplan_dispatch_msgs.msg import ActionDispatch, CompletePlan
from rosplan_knowledge_msgs.srv import GetAttributeService

#################################################################################################################

def call_rosplan_services():
    rospy.wait_for_service("/rosplan_problem_interface/problem_generation_server")
    rospy.wait_for_service("/rosplan_planner_interface/planning_server")

    try:
        # /rosplan_problem_interface/problem_generation_server
        generate_problem = rospy.ServiceProxy("/rosplan_problem_interface/problem_generation_server", Empty) 
        # /rosplan_planner_interface/planning_server
        plan = rospy.ServiceProxy("/rosplan_planner_interface/planning_server", Empty)
        # /rosplan_plan_dispatcher/dispatch_plan
        # dispatch_plan = rospy.ServiceProxy("/rosplan_plan_dispatcher/dispatch_plan", CompletePlan)
        # rosservice call /rosplan_knowledge_base/state/propositions "predicate_name: 'task_failed'" 
        rospy.wait_for_service("/rosplan_knowledge_base/state/propositions")

        print("Calling problem generation...")
        generate_problem()
        time.sleep(10)

        print("Calling planner...")
        plan()
        time.sleep(10)

        print("Dispatching...")
        get_props = rospy.ServiceProxy("/rosplan_knowledge_base/state/propositions", GetAttributeService)
        response = get_props("task_failed")
        for attr in response.attributes:
            if attr.attribute_name == "task_failed":
                print('task_failed: ', attr.is_negative)  # If is_negative == False → task_failed is True
                break
        
        # print("Dispatch the plan...")
        # dispatch_plan()
        # time.sleep(2)

    except rospy.ServiceException as e:
        print(f"Service call failed: {e}")
        
'''
def dispatch_plan_step_by_step(plan):
    pub = rospy.Publisher("/action_dispatch", ActionDispatch, queue_size=10)
    rospy.sleep(1.0)

    for action in plan:
        rospy.loginfo(f"Dispatching action: {action.name} with parameters: {[p.value for p in action.parameters]}")
        pub.publish(action)
        rospy.sleep(3.0)  # Allow time for action execution

        if check_task_failed():
            print("Task_failed is True. Stopping execution.")
            break

def check_task_failed():
    rospy.wait_for_service("/rosplan_knowledge_base/state/propositions")
    get_props = rospy.ServiceProxy("/rosplan_knowledge_base/state/propositions", GetAttributeService)
    result = get_props("task_failed")
    for prop in result.attributes:
        if prop.attribute_name == "task_failed" and not prop.is_negative:
            return True
    return False
'''

##################################################################################################################

def main_gui(domain_path, instance_path):
    instance_name = os.path.splitext(os.path.basename(instance_path))[0]
    alt_path = "./" + instance_name + "_alternative.rddl"
    alt_name = os.path.splitext(os.path.basename(alt_path))[0]
    
    # Initialize rospy after roscore is up
    rospy.init_node("reactive_rosplan", anonymous=True)
    
    # Call planning pipeline
    try:
        call_rosplan_services()
        print("ROSPlan services called.")

    finally:
        print("Shutting down ROSPlan launch process...")

#################################################################################################################
    
def main():
    # Initialize ROSPlan
    subprocess.call(["python3", "start_ros.py"])
    print('DONE!')

#################################################################################################################

if __name__ == "__main__":
    main()
