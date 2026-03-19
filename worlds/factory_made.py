#!/usr/bin/env python3

import os
import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose

# ===== 参数区域 =====
MODEL_NAME = "aws_robomaker_warehouse_ShelfE_01"
MODEL_PATH = os.path.expanduser("~/models/" + MODEL_NAME + "/model.sdf")

X_SPACING = 5.9   # 3.9+2
Y_SPACING = 2.9  # 0.9+2

NUM_X = 3   # X方向数量（可改）
NUM_Y = 5   # Y方向数量（可改）
# =====================

def spawn_model():
    rospy.init_node("spawn_shelf_grid")
    rospy.wait_for_service("/gazebo/spawn_sdf_model")
    spawn = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

    with open(MODEL_PATH, "r") as f:
        model_xml = f.read()

    count = 0

    for i in range(NUM_X):
        for j in range(NUM_Y):
            model_name = f"shelf_{i}_{j}"

            pose = Pose()
            pose.position.x = i * X_SPACING
            pose.position.y = j * Y_SPACING
            pose.position.z = 0
            pose.orientation.w = 1.0

            spawn(model_name,
                  model_xml,
                  "",
                  pose,
                  "world")

            rospy.loginfo(f"Spawned {model_name} at ({pose.position.x}, {pose.position.y})")
            count += 1

    rospy.loginfo(f"Total spawned: {count}")

if __name__ == "__main__":
    spawn_model()