#!/usr/bin/env python3

import os
import rospy
import tf.transformations as tft
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose

# ===== 参数 =====
MODEL_NAME = "desk"
MODEL_PATH = os.path.expanduser("~/models/" + MODEL_NAME + "/model.sdf")

SIZE_X = 1.0   # x方向尺寸
SIZE_Y = 0.7   # y方向尺寸

NUM_X = 4
NUM_Y = 2
GROUP_NUM = 2

GROUP_SPACING = 1.4  # 组间距（y方向）
# =================


def spawn_model():

    rospy.init_node("spawn_desk_groups")
    rospy.wait_for_service("/gazebo/spawn_sdf_model")

    spawn = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

    with open(MODEL_PATH, "r") as f:
        model_xml = f.read()

    count = 0

    group_height = NUM_Y * SIZE_Y

    for g in range(GROUP_NUM):

        # y方向分组
        group_offset_y = g * (group_height + GROUP_SPACING)

        for i in range(NUM_X):
            for j in range(NUM_Y):

                model_name = f"desk_{g}_{i}_{j}"

                pose = Pose()

                # ===== 基础位置 =====
                pose.position.x = i * SIZE_X
                pose.position.y = group_offset_y + j * SIZE_Y
                pose.position.z = 0

                # ===== 姿态（统一用 quaternion）=====
                if j == 1:
                    # 第二列：180°旋转
                    yaw = 3.1415926

                    # ❗补偿（原点在右下角）
                    pose.position.x += SIZE_X
                    pose.position.y += SIZE_Y
                else:
                    yaw = 0.0
                print(f"j={j}, yaw={yaw}")

                q = tft.quaternion_from_euler(0, 0, yaw)

                pose.orientation.x = q[0]
                pose.orientation.y = q[1]
                pose.orientation.z = q[2]
                pose.orientation.w = q[3]

                spawn(model_name, model_xml, "", pose, "world")

                rospy.loginfo(f"Spawned {model_name}")
                count += 1

    rospy.loginfo(f"Total spawned: {count}")


if __name__ == "__main__":
    spawn_model()