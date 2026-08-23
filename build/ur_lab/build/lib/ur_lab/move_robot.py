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
        self.thread = threading.Thread(target=self.run_sequence)
        self.thread.start()
    
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

    # --- HELPER: Sends trajectory goal and blocks until execution is complete ---
    def send_goal(self, points, starttime):
        self.get_logger().info('Preparing joint trajectory goal...')

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
            # We want to give velocity/effort arrays to prevent controller warnings
            p.velocities = [0.0] * 6
            tt += 4
            goal_msg.trajectory.points.append(p)
       
        self.get_logger().info('Sending trajectory goal...')
        
        # We will use this event to block the run_sequence thread
        move_event = threading.Event()
        result_status = {'success': False}

        def goal_response_callback(future):
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().error('Goal rejected by controller')
                move_event.set()
                return

            self.get_logger().info('Goal accepted by controller, waiting for execution...')
            result_future = goal_handle.get_result_async()
            
            # Setup callback for when execution finishes
            def result_callback(future_res):
                result = future_res.result().result
                self.get_logger().info(f'Trajectory finished with error code: {result.error_code}')
                if result.error_code == 0:
                    result_status['success'] = True
                move_event.set()

            result_future.add_done_callback(result_callback)

        send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(goal_response_callback)

        # Block here until execution is complete
        move_event.wait()
        return result_status['success']

    def feedback_callback(self, feedback_msg):
        pass

    # --- SEQUENCE SCENARIO (Runs sequentially step-by-step) ---
    def run_sequence(self):
        self.get_logger().info("--- Sequence Started ---")

        # 1. Move to home position (blocks until finished)
        points1 = [
            [-0.226893, -1.24, 1.45, -1.52, -1.62, -0.20944],
            [0.0174533, -1.16937, 1.41372, -1.5708, -1.55334, 0.0349066],
            [0.0174533, -0.890118, 1.01229, -1.44862, -1.55334, 0.0349066],
            [0.0174533, -1.16937, 1.41372, -1.5708, -1.55334, 0.0349066],
            [-0.226893, -1.24, 1.45, -1.52, -1.62, -0.20944],
            [-0.174533, -0.767945, 0.837758, -1.36136, -1.62, -0.174533],
             [0.15708, -0.610865, 0.541052, -1.23918, -1.51844, 0.15708],
            [-0.541052, -0.506145, 0.366519, -1.18682, -1.71042, -0.523599],
           # [-0.174533, -0.767945, 0.837758, -1.36136, -1.62, -0.174533],
        ]
        self.get_logger().info("Executing First Move Sequence...")
        self.send_goal(points1, 4)
       
        # 2. Spawn a RED cube (blocks until spawned)
        self.get_logger().info("Spawning Red Cube...")
        self.spawn_cube("seq_cube_red", x=0.75, y=-0.15, z=0.4, color_rgba="1 0 0 1")

        # 3. Move to another location (blocks until finished)
        points2 = [
          [-0.64577182,-0.9424778,1.15191731,-1.55334303,-1.72787596,-0.61086524],
          [-0.57595865,-1.01229097,1.23918377,-1.58824962,-1.71042267,-0.55850536],
          [-0.54105207,-0.89011792,1.11701072,-1.8675023,-1.51843645,-0.54105207],
          [ 0.19198622,-0.89011792,1.11701072,-1.8675023,-1.58824962,0.19198622],
          [-0.05235988,-0.99483767,1.29154365,-1.93731547,-1.57079633,-0.05235988]


         # [ 0.34906585,-0.80285146,0.90757121,-1.41371669,-1.48352986,0.33161256]
        ]
        self.get_logger().info("Executing Second Move Sequence...")
        self.send_goal(points2, 4)  # Notice starttime reset to 4 since it's a new, clean goal message

        #4. Spawn a BLUE cube (blocks until spawned)
        self.get_logger().info("Spawning Blue Cube...")
        self.spawn_cube("seq_cube_blue", x=0.8, y=-0.1, z=0.4, color_rgba="0 0 1 1")

        points3 = [
          [-0.05235988,-0.802851,0.9424778,-1.72787596,-1.57079633,-0.05235988],
          [-0.55850536,-0.59341195,0.55850536,-1.55334303,-1.57079633,-0.55850536],
          [ 0.06981317,-0.75049158,0.87266463,-1.69296937,-1.58824962,0.06981317]
        ]
        self.get_logger().info("Executing Second Move Sequence...")
        self.send_goal(points3, 4)  

        self.get_logger().info("Spawning 3rd Cube...")
        self.spawn_cube("seq_cube_3", x=0.8, y=-0.12, z=0.4, color_rgba="0 0 1 1")

        points4 = [
         # [ 0.06981317,-0.75049158,0.87266463,-1.69296937,-1.58824962,0.06981317],
          [-0.45378561,-0.71558499,0.80285146,-1.65806279,-1.57079633,-0.45378561],
          [-0.2443461,-0.82030475,0.97738438,-1.72787596,-1.57079633,-0.2443461 ]

        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points4, 4)  

        self.get_logger().info("Spawning 4th Cube...")
        self.spawn_cube("seq_cube_4", x=0.86, y=0.1, z=0.4, color_rgba="1 0 0 1")

        points5 = [
            [-0.2268928,-0.61086524,0.57595865,-1.55334303,-1.57079633,-0.2268928],
            [ 0.       ,-0.57595865,0.48869219,-1.51843645,-1.57079633,0.        ],
            [ 0.10471976,-0.55850536,0.48869219,-1.51843645,-1.57079633,0.10471976],
            [-0.08726646,-1.11701072,1.46607657,-1.91986218,-1.57079633,-0.08726646]
         
        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points5, 4)  

        self.get_logger().info("Spawning 5th Cube...")
        self.spawn_cube("seq_cube_5", x=0.75, y=-0.1, z=0.4, color_rgba="1 0 0 1")

        points6 = [
            [-0.08726646,-1.25663706,1.67551608,-1.98967535,-1.57079633,-0.08726646],
            [-0.57595865,-1.1693706,1.55334303,-1.95476876,-1.57079633,-0.57595865],
            [-0.4712389,-0.83775804,1.01229097,-1.74532925,-1.57079633,-0.4712389],
            [-0.08726646,-0.9250245,1.15191731,-1.79768913,-1.57079633,-0.08726646],
            [ 0.05235988,-0.87266463,1.08210414,-1.78023584,-1.57079633,0.05235988],
            [ 0.08726646,-0.85521133,1.04719755,-1.76278254,-1.57079633,0.08726646],
            [-0.20943951,-0.9250245,1.1693706,-1.81514242,-1.57079633,-0.20943951]
        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points6, 4)  

        self.get_logger().info("Spawning 6th Cube...")
        self.spawn_cube("seq_cube_6", x=0.8, y=0.1, z=0.4, color_rgba="1 0 0 1")

        points7 = [
            [-0.19198622,-0.82030475,0.99483767,-1.74532925,-1.57079633,-0.19198622],
            [0.05235988,-0.76794487,0.89011792,-1.69296937,-1.57079633,0.05235988],
            [-0.26179939,-1.11701072,1.48352986,-1.93731547,-1.57079633,-0.26179939]
        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points7, 4)  

        
        self.get_logger().info("Spawning 7th Cube...")
        self.spawn_cube("seq_cube_7", x=0.8, y=0.05, z=0.4, color_rgba="0 0 1 1")

        points8 = [
            [0.01745329,-1.08210414,1.43116999,-1.91986218,-1.57079633,0.01745329],
            [ 0.01745329,-0.75049158,0.87266463,-1.69296937,-1.57079633,0.01745329],
            [-0.34906585,-0.75049158,0.80285146,-1.69296937,-1.57079633,-0.34906585],
            [-0.41887902,-0.6981317,0.78539816,-1.65806279,-1.57079633,-0.41887902],
            [-0.26179939,-1.29154365,1.72787596,-2.00712864,-1.57079633,-0.26179939]


        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points8, 4)  

        self.get_logger().info("Spawning 8th Cube...")
        self.spawn_cube("seq_cube_8", x=0.6, y=-0.20, z=0.4, color_rgba="0 0 1 1")

        points8 = [
           # [-0.45378561,-0.4712389,1.71042267,-2.00712864,-1.57079633,-0.45378561],
            [-0.71558499,-1.11701072,1.48352986,-1.93731547,-1.57079633,-0.71558499],
            [-0.82030475,-1.29154365,1.72787596,-2.00712864,-1.57079633,-0.82030475],
            [-0.87266463,-1.22173048,1.6406095,-1.98967535,-1.57079633,-0.87266463],
            [-0.6981317,-0.90757121,1.15191731,-1.81514242,-1.57079633,-0.6981317 ],
            [0.0, -1.5708, 0.0, -1.5708, 0.0, 0.0],
        ]
        self.get_logger().info("Executing Move Sequence...")
        self.send_goal(points8, 4)  

        self.get_logger().info("--- Sequence Finished! ---")
        rclpy.shutdown()



def main(args=None):
    rclpy.init(args=args)
    node = MoveRobotSequence()
    rclpy.spin(node)


if __name__ == '__main__':
    main()
