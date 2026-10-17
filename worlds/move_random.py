#!/usr/bin/env python3

import rospy
import random
import math

from gazebo_msgs.srv import (
    SetModelState,
    GetModelState,
    SpawnModel
)

from gazebo_msgs.msg import (
    ModelState,
    ModelStates
)

from geometry_msgs.msg import (
    Pose,
    Twist
)

# =========================================================
# ENVIRONMENT CONFIG
# =========================================================

CONFIG = {

    'num_obstacles': 40,

    'x_min': 0.5,
    'x_max': 14.0,

    'y_min': -4.0,
    'y_max': 4.0,

    'min_speed': 0.6,
    'max_speed': 1.0,

    
    'radius': 0.15,
    'length': 0.4,
    'height': 0.2,

    'rate': 20,
    'respawn_time_window': 4.0,   # T秒
    'min_y_gap': 0.8,            # 最小y间隔
}

# =========================================================
# CYLINDER MODEL
# =========================================================
SPACING = 1.0

DEFAULT_CYLINDER_SDF = """<?xml version="1.0" ?>
<sdf version="1.6">

<model name="{model_name}">

  <static>false</static>

  <kinematic>true</kinematic>

  <link name="link">
    <gravity>false</gravity>
    <collision name="collision">

      <geometry>
        <cylinder>
          <radius>{radius}</radius>
          <length>{length}</length>
        </cylinder>
      </geometry>

      <surface>

        <contact>

          <collide_without_contact>true</collide_without_contact>

        </contact>

      </surface>

    </collision>

    <visual name="visual">

      <geometry>
        <cylinder>
          <radius>{radius}</radius>
          <length>{length}</length>
        </cylinder>
      </geometry>

      <material>
        <ambient>0.2 0.8 0.2 1</ambient>
        <diffuse>0.2 0.8 0.2 1</diffuse>
      </material>

    </visual>

    <inertial>
      <mass>1.0</mass>
    </inertial>

  </link>

</model>
"""

# =========================================================
# ???????
# =========================================================
def generate_random_obstacle(index):

    x = random.uniform(
        CONFIG['x_min'],
        CONFIG['x_max']
    )

    # ?????????
    y = random.uniform(CONFIG['y_min'], CONFIG['y_max'])

    speed = random.uniform(
        CONFIG['min_speed'],
        CONFIG['max_speed']
    )

    vx = -speed
    vy = 0.0

    return {

        'name': f'obstacle_{index+1}',

        'x': x,
        'y': y,

        'vx': vx,
        'vy': vy,

        'height': CONFIG['height'],
        'length': CONFIG['length'],
        'radius': CONFIG['radius'],
    }
#=============

def create_random_models():

    models = []

    for i in range(CONFIG['num_obstacles']):
        models.append(
            generate_random_obstacle(i)
        )

    return models

# =========================================================
# ??SDF
# =========================================================

def load_model_xml(model_name, length, radius):

    return DEFAULT_CYLINDER_SDF.format(
        model_name=model_name,
        radius=radius,
        length=length
    )

# =========================================================
# ??????
# =========================================================

def ensure_model_exists(model):

    rospy.wait_for_service(
        '/gazebo/get_model_state'
    )

    get_model_state = rospy.ServiceProxy(
        '/gazebo/get_model_state',
        GetModelState
    )

    try:

        resp = get_model_state(
            model['name'],
            'world'
        )

        if resp.success:

            rospy.loginfo(
                "%s already exists",
                model['name']
            )

            return

    except:
        pass

    rospy.loginfo(
        "Spawning %s",
        model['name']
    )

    rospy.wait_for_service(
        '/gazebo/spawn_sdf_model'
    )

    spawn_model = rospy.ServiceProxy(
        '/gazebo/spawn_sdf_model',
        SpawnModel
    )

    pose = Pose()

    pose.position.x = model['x']
    pose.position.y = model['y']
    pose.position.z = model['height']

    model_xml = load_model_xml(
        model['name'],
        model['length'],
        model['radius']
    )

    spawn_model(
        model['name'],
        model_xml,
        '',
        pose,
        'world'
    )
def generate_respawn_y(spawn_history):

    now = rospy.get_time()

    # 删除超过时间窗口的记录
    spawn_history[:] = [
        item for item in spawn_history
        if now - item[0] < CONFIG['respawn_time_window']
    ]

    for _ in range(100):

        candidate_y = random.uniform(
            CONFIG['y_min'],
            CONFIG['y_max']
        )

        valid = True

        for _, y in spawn_history:

            if abs(candidate_y - y) < CONFIG['min_y_gap']:

                valid = False
                break

        if valid:

            spawn_history.append(
                (now, candidate_y)
            )

            return candidate_y

    # 极端情况下直接返回
    candidate_y = random.uniform(
        CONFIG['y_min'],
        CONFIG['y_max']
    )

    spawn_history.append(
        (now, candidate_y)
    )

    return candidate_y
# =========================================================
# ???
# =========================================================

def main():

    rospy.init_node(
        'dynamic_obstacle_environment'
    )

    rospy.loginfo(
        "Waiting Gazebo clock..."
    )

    while (
        rospy.Time.now().to_sec() == 0
        and not rospy.is_shutdown()
    ):
        rospy.sleep(0.1)

    rospy.loginfo(
        "Gazebo clock ready"
    )

    rospy.sleep(1.0)

    # ???????
    models = create_random_models()
    spawn_history = []
    rospy.wait_for_service(
        '/gazebo/set_model_state'
    )

    set_state = rospy.ServiceProxy(
        '/gazebo/set_model_state',
        SetModelState
    )
    obstacle_pub = rospy.Publisher(
        '/dynamic_obstacle_states',
        ModelStates,
        queue_size=1
    )
    # ????
    for model in models:

        ensure_model_exists(model)

    rospy.loginfo(
        "All obstacles spawned"
    )

    rate = rospy.Rate(
        CONFIG['rate']
    )
    last_time = rospy.Time.now().to_sec()
    # dt = 1.0 / CONFIG['rate']

    # =====================================================
    # ???
    # =====================================================

    while not rospy.is_shutdown():
        now = rospy.Time.now().to_sec()
        dt = now - last_time
        last_time = now
        obstacle_states = ModelStates()
        for model in models:

            # ????
            model['x'] += model['vx'] * dt
            model['y'] += model['vy'] * dt

            # ==========================
            # X????
            # ==========================

            if model['x'] <= CONFIG['x_min']:

                model['x'] = CONFIG['x_max']

                model['y'] = generate_respawn_y(
                    spawn_history
                )

                speed = random.uniform(
                    CONFIG['min_speed'],
                    CONFIG['max_speed']
                )

                model['vx'] = -speed
                model['vy'] = 0.0
            # ==========================
            # Y????
            # ==========================

            if model['y'] <= CONFIG['y_min']:

                model['y'] = CONFIG['y_min']
                model['vy'] *= -1

            elif model['y'] >= CONFIG['y_max']:

                model['y'] = CONFIG['y_max']
                model['vy'] *= -1

            # ==========================
            # Gazebo????
            # ==========================

            state = ModelState()

            state.model_name = model['name']
            state.reference_frame = 'world'

            state.pose.position.x = model['x']
            state.pose.position.y = model['y']
            state.pose.position.z = model['height']

            state.pose.orientation.x = 0.0
            state.pose.orientation.y = 0.0
            state.pose.orientation.z = 0.0
            state.pose.orientation.w = 1.0

            state.twist.linear.x = 0.0
            state.twist.linear.y = 0.0
            state.twist.linear.z = 0.0

            state.twist.angular.x = 0.0
            state.twist.angular.y = 0.0
            state.twist.angular.z = 0.0

            try:

                set_state(state)

            except rospy.ServiceException as e:

                rospy.logwarn(e)
            
            pose = Pose()
            pose.position.x = model['x']
            pose.position.y = model['y']
            pose.position.z = model['height']

            pose.orientation.x = 0.0
            pose.orientation.y = 0.0
            pose.orientation.z = 0.0
            pose.orientation.w = 1.0

            twist = Twist()

            twist.linear.x = model['vx']
            twist.linear.y = model['vy']
            twist.linear.z = 0.0

            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = 0.0

            obstacle_states.name.append(
                model['name']
            )

            obstacle_states.pose.append(
                pose
            )

            obstacle_states.twist.append(
                twist
            )
        obstacle_pub.publish(
        obstacle_states
        )
        rate.sleep()

# =========================================================

if __name__ == '__main__':

    try:

        main()

    except rospy.ROSInterruptException:

        pass