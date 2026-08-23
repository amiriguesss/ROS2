
import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from gazebo_msgs.srv import SpawnEntity


class MoveRobot(Node):

    def __init__(self):
        super().__init__('move_robot')

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        # Service client for spawning cubes
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')

        # Wait for connections
        self.get_logger().info('Waiting for trajectory controller...')
        self.traj_client.wait_for_server()

        self.get_logger().info('Waiting for Gazebo spawn service...')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not ready yet...')

        self.send_goal()