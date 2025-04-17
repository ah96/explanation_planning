#!/usr/bin/env python

import rospy
from rosplan_knowledge_msgs.srv import GetAttributeService
from rosplan_knowledge_msgs.msg import KnowledgeItem

def get_is_negative_value(predicate_name='task_failed'):
    rospy.wait_for_service('/rosplan_knowledge_base/state/propositions')
    try:
        get_propositions = rospy.ServiceProxy('/rosplan_knowledge_base/state/propositions', GetAttributeService)
        response = get_propositions(predicate_name)
        
        if response.attributes:
            for attr in response.attributes:
                if attr.attribute_name == predicate_name:
                    return attr.is_negative
        else:
            rospy.logwarn("No attributes found for predicate: %s", predicate_name)
            return None
    except rospy.ServiceException as e:
        rospy.logerr("Service call failed: %s", e)
        return None

if __name__ == "__main__":
    rospy.init_node('get_is_negative_checker')
    is_neg = get_is_negative_value()
    if is_neg is not None:
        print(f"is_negative value for 'task_failed': {is_neg}")
    else:
        print("Could not retrieve is_negative value.")
