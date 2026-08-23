#!/usr/bin/env python3
import rospy
from gazebo_msgs.srv import SpawnModel
from geometry_msgs.msg import Pose

rospy.init_node("spawn_cube_node")

rospy.wait_for_service("/gazebo/spawn_sdf_model")
spawn_model = rospy.ServiceProxy("/gazebo/spawn_sdf_model", SpawnModel)

cube_sdf = """
<?xml version="1.0" ?>
<sdf version="1.6">
  <model name="middle_cube">
    <pose>0 0 0 0 0 0</pose>
    <link name="link">
      <inertial>
        <mass>1.0</mass>
        <inertia>
          <ixx>0.0004</ixx>
          <iyy>0.0004</iyy>
          <izz>0.0004</izz>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyz>0</iyz>
        </inertia>
      </inertial>

      <collision name="collision">
        <geometry>
          <box>
            <size>0.05 0.05 0.05</size>
          </box>
        </geometry>
      </collision>

      <visual name="visual">
        <geometry>
          <box>
            <size>0.05 0.05 0.05</size>
          </box>
        </geometry>
        <material>
          <ambient>0.8 0.2 0.2 1</ambient>
          <diffuse>0.8 0.2 0.2 1</diffuse>
        </material>
      </visual>
    </link>
  </model>
</sdf>
"""

pose = Pose()
pose.position.x = 0.0
pose.position.y = 0.0
pose.position.z = 0.6

spawn_model(
    model_name="middle_cube",
    model_xml=cube_sdf,
    robot_namespace="",
    initial_pose=pose,
    reference_frame="world",
)

print("Cube spawned")
