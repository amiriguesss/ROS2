#!/usr/bin/env python3

import threading
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from gazebo_msgs.srv import SpawnEntity

class MoveRobotSequence(Node):

    def __init__(self):
        super().__init__('move_robot')

        # Action client for moving the robot
        self._action_client = ActionClient(
            self,
            FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )

        # Service client for spawning cubes
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')

        # Wait for connections
        self.get_logger().info('Waiting for trajectory controller...')
        self._action_client.wait_for_server()

        self.get_logger().info('Waiting for Gazebo spawn service...')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not ready yet...')

        # Start the sequence in a separate thread to avoid blocking ROS callbacks
        # self.thread = threading.Thread(target=self.run_sequence)
        # self.thread.start()
        self.run_sequence()
    # --- HELPER: Moves the robot to target joint angles and waits until it arrives ---
    def move_to(self, positions, duration):
        self.get_logger().info(f"Moving to: {positions}")
        
        goal = FollowJointTrajectory.Goal()
        goal.trajectory.joint_names = [
            'shoulder_pan_joint',
            'shoulder_lift_joint',
            'elbow_joint',
            'wrist_1_joint',
            'wrist_2_joint',
            'wrist_3_joint'
        ]
        
        point = JointTrajectoryPoint()
        point.positions = positions
        point.time_from_start.sec = duration
        goal.trajectory.points.append(point)

        stamp = self.get_clock().now().to_msg()
        stamp.sec += 1
        goal.trajectory.header.stamp = stamp

        event = threading.Event()
        self.traj_success = False

        def result_callback(future):
            nonlocal event
            result = future.result().result
            if result.error_code == 0:
                self.traj_success = True
            else:
                self.get_logger().error(f"Move failed with error: {result.error_code}")
            event.set()

        def goal_response_callback(future):
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().error('Movement rejected')
                event.set()
                return
            res_future = goal_handle.get_result_async()
            res_future.add_done_callback(result_callback)

        future = self.traj_client.send_goal_async(goal)
        future.add_done_callback(goal_response_callback)

        # Pause thread execution until the movement is finished
        event.wait()
        return self.traj_success

    # --- HELPER: Spawns a cube and waits until Gazebo finishes spawning it ---
    def spawn_cube(self, name, x, y, z, color_rgba="1 0 0 1"):
        self.get_logger().info(f"Spawning {name} at x={x}, y={y}")
        
        cube_sdf = f"""<?xml version="1.0" ?>
        <sdf version="1.6">
          <model name="{name}">
            <static>false</static>
            <link name="link">
              <inertial>
                <mass>0.1</mass>
                <inertia><ixx>0.0001</ixx><iyy>0.0001</iyy><izz>0.0001</izz></inertia>
              </inertial>
              <collision name="collision">
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
              </collision>
              <visual name="visual">
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
                <material>
                  <ambient>{color_rgba}</ambient>
                  <diffuse>{color_rgba}</diffuse>
                </material>
              </visual>
            </link>
          </model>
        </sdf>
        """

        req = SpawnEntity.Request()
        req.name = name
        req.xml = cube_sdf
        req.reference_frame = 'world'
        req.initial_pose.position.x = x
        req.initial_pose.position.y = y
        req.initial_pose.position.z = z
        req.initial_pose.orientation.w = 1.0

        event = threading.Event()
        self.spawn_success = False

        def spawn_callback(future):
            nonlocal event
            try:
                res = future.result()
                self.spawn_success = res.success
                if not res.success:
                    self.get_logger().error(f"Spawn error message: {res.status_message}")
            except Exception as e:
                self.get_logger().error(f"Service call failed: {e}")
            event.set()

        future = self.spawn_client.call_async(req)
        future.add_done_callback(spawn_callback)

        # Pause thread execution until spawn is finished
        event.wait()
        return self.spawn_success

    
    def send_goal(self,points,starttime):
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
        tt = starttime
        for i in points:
            p = JointTrajectoryPoint()
            p.positions = i
            p.time_from_start.sec = tt
            tt += 4
            goal_msg.trajectory.points.append(p)
       
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

    # --- YOUR SEQUENCE FUNCTION (Write your scenario here) ---
    def run_sequence(self):
        self.get_logger().info("--- Sequence Started ---")




        points1 = [[-0.226893,-1.24,1.45,-1.52,-1.62,-0.20944],
                    [0.0174533,-1.16937,1.41372,-1.5708,-1.55334,0.0349066],
                    [0.0174533,-0.890118,1.01229,-1.44862,-1.55334,0.0349066],
                    [0.0174533,-1.16937,1.41372,-1.5708,-1.55334,0.0349066],
                    [-0.226893,-1.24,1.45,-1.52,-1.62,-0.20944],
                    [-0.174533,-0.767945,0.837758,-1.36136,-1.62,-0.174533]
        ]
 
        ok = self.send_goal(points1,4)
        # 1. Move to home position
        #self.move_to([0.0, -1.2, 1.4, -1.5, -1.57, 0.0], duration=4)

        # 2. Spawn a RED cub

        self.spawn_cube("seq_cube_red", x=0.9, y=0.1, z=0.4, color_rgba="1 0 0 1")

        points2 = [[0.15708,-0.610865,0.541052,-1.23918,-1.51844,0.15708],
                    [-0.541052,-0.506145, 0.366519,-1.18682,-1.71042,-0.523599],
                    [-0.174533,-0.767945,0.837758,-1.36136,-1.62,-0.174533],
                    [0.0,-1.5708,0.0,-1.5708,0.0,0.0]]

        ok = self.send_goal(points2,32)
        # # 3. Move to another location
        # self.move_to([0.3, -1.1, 1.3, -1.6, -1.57, 0.0], duration=10)

        # # 4. Spawn a BLUE cube
        # self.spawn_cube("seq_cube_blue", x=0.6, y=-0.1, z=0.05, color_rgba="0 0 1 1")

        # # 5. Move to final location
        # self.move_to([-0.3, -1.2, 1.4, -1.5, -1.57, 0.0], duration=5)

        # # 6. Spawn a GREEN cube
        # self.spawn_cube("seq_cube_green", x=0.5, y=0.0, z=0.05, color_rgba="0 1 0 1")

        # # 7. Go back home
        # self.move_to([0.0, -1.2, 1.4, -1.5, -1.57, 0.0], duration=4)

        self.get_logger().info("--- Sequence Finished! ---")
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = MoveRobotSequence()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
