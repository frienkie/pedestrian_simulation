#!/usr/bin/env python3

import os
import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose

# ===== 参数区域 =====
MODEL_NAME = "desk_drawer"
MODEL_PATH = os.path.expanduser("~/.gazebo/models/" + MODEL_NAME + "/model.sdf")

DESK_LENGTH = 1.83
DESK_WIDTH  = 0.53

GROUP_SPACING = 1.4

X_SPACING = DESK_WIDTH
Y_SPACING = DESK_LENGTH

GROUP_NUM = 2
NUM_X = 2
NUM_Y = 3
# =====================


def spawn_model():

    rospy.init_node("spawn_desk_groups")
    rospy.wait_for_service("/gazebo/spawn_sdf_model")

    spawn = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

    with open(MODEL_PATH, "r") as f:
        model_xml = f.read()

    count = 0

    group_width = NUM_X * DESK_WIDTH

    for g in range(GROUP_NUM):

        group_offset_x = g * (group_width + GROUP_SPACING)

        for i in range(NUM_X):
            for j in range(NUM_Y):

                model_name = f"desk_{g}_{i}_{j}"

                pose = Pose()
                pose.position.x = group_offset_x + i * X_SPACING
                pose.position.y = j * Y_SPACING
                pose.position.z = 0

                # 抽屉朝外
                if i%2 == 0:
                    pose.orientation.z = -1.0
                # else:
                #     pose.orientation.z = 1.0
                #     pose.orientation.w = 0.0

                spawn(model_name,
                      model_xml,
                      "",
                      pose,
                      "world")

                rospy.loginfo(f"Spawned {model_name}")
                count += 1

    rospy.loginfo(f"Total spawned: {count}")


if __name__ == "__main__":
    spawn_model()