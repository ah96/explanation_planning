#!/usr/bin/env python
import rospy
from rosplan_dispatch_msgs.msg import ActionDispatch
from rosplan_dispatch_msgs.srv import GetPlanService

def dispatch_action(action):
    pub = rospy.Publisher('/action_dispatch', ActionDispatch, queue_size=10)
    rospy.sleep(1.0)
    rospy.loginfo(f"Dispatching: {action.name}")
    pub.publish(action)

if __name__ == '__main__':
    rospy.init_node('step_by_step_dispatcher')

    rospy.wait_for_service('/rosplan_planner_interface/planning_server')
    rospy.wait_for_service('/rosplan_parsing_interface/get_plan')
    from rosplan_dispatch_msgs.srv import GetPlanService
    get_plan = rospy.ServiceProxy('/rosplan_parsing_interface/get_plan', GetPlanService)

    # Generate plan
    rospy.loginfo("Requesting plan...")
    rospy.ServiceProxy('/rosplan_planner_interface/planning_server', Empty)()

    rospy.sleep(2.0)  # wait for plan generation

    plan_response = get_plan()
    rospy.loginfo(f"Got plan with {len(plan_response.plan)} actions.")

    for action in plan_response.plan:
        dispatch_action(action)
        raw_input("Press Enter to dispatch next action...")
