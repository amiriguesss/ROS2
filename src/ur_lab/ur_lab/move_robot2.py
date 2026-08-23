#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint


class MoveRobot(Node):

    def __init__(self):
        super().__init__('move_robot')

        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        self.send_goal()

    def send_goal(self):
        self.get_logger().info('Waiting for joint trajectory controller...')

        self._action_client.wait_for_server()

        goal_msg = FollowJointTrajectory.Goal()

        goal_msg.trajectory.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]

        p1 = JointTrajectoryPoint()

        # Joint target positions in radians
        p1.positions = [
            -0.226893,
            -1.24,
            1.45,
            -1.52,
            -1.62,
            -0.20944
        ]

        # Optional velocities
        p1.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]
        p1.time_from_start.sec = 4

        p7 = JointTrajectoryPoint()
        p7.positions = [
            0.0174533,
            -1.16937,
            1.41372,
            -1.5708,
            -1.55334,
            0.0349066


        ]
        p7.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]
        p7.time_from_start.sec = 8

        p8 = JointTrajectoryPoint()
        p8.positions = [
            0.0174533,
            -0.890118,
            1.01229,
            -1.44862,
            -1.55334,
            0.0349066

        ]
        p8.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]
        p8.time_from_start.sec = 12

        p9 = JointTrajectoryPoint()
        p9.positions = [
            0.0174533,
            -1.16937,
            1.41372,
            -1.5708,
            -1.55334,
            0.0349066


        ]
        p9.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]
        p9.time_from_start.sec = 16

        p10 = JointTrajectoryPoint()
        p10.positions = [
            -0.226893,
            -1.24,
            1.45,
            -1.52,
            -1.62,
            -0.20944
        ]
        p10.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0
        ]
        p10.time_from_start.sec = 20

        p2 = JointTrajectoryPoint()
        p2.positions = [
            -0.174533,
            -0.767945,
            0.837758,
            -1.36136,
            -1.62,
            -0.174533
        ]
        p2.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0]
        p2.time_from_start.sec = 24

        p3 = JointTrajectoryPoint()
        p3.positions = [
            0.15708,
            -0.610865,
            0.541052,
            -1.23918,
            -1.51844,
            0.15708
        ]
        p3.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0]
        p3.time_from_start.sec = 28
        
        p4 = JointTrajectoryPoint()
        p4.positions = [
            -0.541052,
            -0.506145,
             0.366519,
            -1.18682,
            -1.71042,
            -0.523599
        ]
        p4.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0]
        p4.time_from_start.sec = 32
        
        p5 = JointTrajectoryPoint()
        p5.positions = [
            -0.174533,
            -0.767945,
            0.837758,
            -1.36136,
            -1.62,
            -0.174533
        ]
        p5.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0]
        p5.time_from_start.sec = 36
        
        p6 = JointTrajectoryPoint()
        p6.positions = [
            0.0,
            -1.5708,
            0.0,
            -1.5708,
            0.0,
            0.0
        ]
        p6.velocities = [
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0]
        p6.time_from_start.sec = 40

        goal_msg.trajectory.points.append(p1)
        goal_msg.trajectory.points.append(p7)
        goal_msg.trajectory.points.append(p8)
        goal_msg.trajectory.points.append(p9)
        goal_msg.trajectory.points.append(p10)
        goal_msg.trajectory.points.append(p2)
        goal_msg.trajectory.points.append(p3)
        goal_msg.trajectory.points.append(p4)
        goal_msg.trajectory.points.append(p5)
        goal_msg.trajectory.points.append(p6)
        self.get_logger().info('Sending trajectory goal...')

        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by controller')
            return

        self.get_logger().info('Goal accepted')

        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Trajectory finished with error code: {result.error_code}')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        pass


def main(args=None):
    rclpy.init(args=args)
    node = MoveRobot()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
