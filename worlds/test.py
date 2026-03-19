#!/usr/bin/env python3

import os
import rospy
import tf.transformations as tft
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose

MODEL_NAME = "desk"
MODEL_PATH = os.path.expanduser("~/model_editor_models/" + MODEL_NAME + "/model.sdf")


def spawn_test():

    rospy.init_node("spawn_rotation_test")
    rospy.wait_for_service("/gazebo/spawn_sdf_model")

    spawn = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

    with open(MODEL_PATH, "r") as f:
        model_xml = f.read()

    # ===== 测试三个角度 =====
    tests = [
        ("desk_0deg", 0.0, 0.0),
        ("desk_90deg", 2.0, 1.5708),
        ("desk_180deg", 4.0, 3.1415926),
    ]

    for name, x, yaw in tests:

        pose = Pose()
        pose.position.x = x
        pose.position.y = 0
        pose.position.z = 0

        # quaternion
        q = tft.quaternion_from_euler(0, 0, yaw)
        pose.orientation.x = q[0]
        pose.orientation.y = q[1]
        pose.orientation.z = q[2]
        pose.orientation.w = q[3]

        spawn(name, model_xml, "", pose, "world")

        rospy.loginfo(f"Spawned {name} with yaw={yaw}")

    rospy.loginfo("Test complete!")


if __name__ == "__main__":
    spawn_test()