#!/usr/bin/env python3
"""
pick_cube: spawn ONE cube, grasp it with the 2-finger gripper,
lift it up and stop when it reaches TARGET_CUBE_Z.

Arm motion uses analytic UR5e IK: you give Cartesian (x, y, z) targets,
the node computes exact joint angles - no hand-tuned waypoint guessing.
"""

import math
import threading

import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile

from control_msgs.action import FollowJointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from gazebo_msgs.srv import SpawnEntity
from gazebo_msgs.msg import ModelStates
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64MultiArray, String
from controller_manager_msgs.srv import (
    ListControllers,
    LoadController,
    ConfigureController,
    SwitchController,
)

JOINTS = [
    'shoulder_pan_joint',
    'shoulder_lift_joint',
    'elbow_joint',
    'wrist_1_joint',
    'wrist_2_joint',
    'wrist_3_joint'
]

# ================== TUNING CONSTANTS ==================
CUBE_NAME = 'pick_cube'
CUBE_X, CUBE_Y, CUBE_Z = 0.75, 0.0, 0.4   # spawn pose (falls onto table)
TARGET_CUBE_Z = 0.45                       # lift stops once cube center is here
LIFT_STEP = 0.02                           # meters per lift step
MAX_LIFT_STEPS = 8
GRIP_OPEN = [0.0, 0.0]
GRIP_CLOSED = [0.0055, 0.0055]             # close onto the already-locked cube
GRASP_TOOL_Z_OFFSET = 0.077                # long fingers cover the whole cube face (tips ~2mm above table)

HOME_Q = [0.0, -1.5708, 0.0, -1.5708, 0.0, 0.0]
SETTLE_BEFORE_LIFT = 2.0                   # seconds to let vibrations die after closing

# ================== UR5e KINEMATICS ==================
D = [0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996]
A = [0.0, -0.425, -0.3922, 0.0, 0.0, 0.0]
ALPHA = [math.pi / 2, 0.0, 0.0, math.pi / 2, -math.pi / 2, 0.0]
# UR DH base frame vs URDF/world frame differ by Rz(pi):
FLIP = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]], dtype=float)


def dh(theta, d, a, alpha):
    ct, st = math.cos(theta), math.sin(theta)
    ca, sa = math.cos(alpha), math.sin(alpha)
    return np.array([
        [ct, -st * ca, st * sa, a * ct],
        [st, ct * ca, -ct * sa, a * st],
        [0.0, sa, ca, d],
        [0.0, 0.0, 0.0, 1.0]])


def fk(q):
    T = np.eye(4)
    for i in range(6):
        T = T @ dh(q[i], D[i], A[i], ALPHA[i])
    return T


def rot_down():
    """desired tool orientation: flange z pointing straight down"""
    return np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=float)


def rot_err_vec(R_des, R_cur):
    A_ = R_des @ R_cur.T
    c = max(-1.0, min(1.0, (np.trace(A_) - 1.0) / 2.0))
    ang = math.acos(c)
    if ang < 1e-8:
        return np.zeros(3)
    w = np.array([A_[2, 1] - A_[1, 2], A_[0, 2] - A_[2, 0], A_[1, 0] - A_[0, 1]])
    return (w / (2.0 * math.sin(ang))) * ang


def jacobian(q, eps=1e-6):
    J = np.zeros((6, 6))
    T0 = fk(q)
    p0, R0 = T0[:3, 3], T0[:3, :3]
    for j in range(6):
        qp = list(q)
        qp[j] += eps
        Tp = fk(qp)
        J[:3, j] = (Tp[:3, 3] - p0) / eps
        J[3:, j] = rot_err_vec(Tp[:3, :3], R0) / eps
    return J


def ik(q_seed, p_world, tol_p=1e-4, tol_r=1e-3, iters=200):
    """damped least squares IK, tool pointing down, returns (q, ok)"""
    p_t = FLIP @ np.asarray(p_world, float)
    R_t = FLIP @ rot_down()
    q = np.array(q_seed, float)
    lm = 0.05
    for _ in range(iters):
        T = fk(q)
        e = np.concatenate([p_t - T[:3, 3], rot_err_vec(R_t, T[:3, :3])])
        if np.linalg.norm(e[:3]) < tol_p and np.abs(e[3:]).max() < tol_r:
            return list(q), True
        J = jacobian(q)
        dq = J.T @ np.linalg.solve(J @ J.T + (lm ** 2) * np.eye(6), e)
        n = np.linalg.norm(dq)
        if n > 0.3:
            dq *= 0.3 / n
        q = np.clip(q + dq, -math.pi, math.pi)
    T = fk(q)
    ok = np.linalg.norm(p_t - T[:3, 3]) < 1e-3
    return list(q), ok


def lerp(qa, qb, t):
    return [a + (b - a) * t for a, b in zip(qa, qb)]


class PickCube(Node):

    # subclasses (e.g. scan_pick) reuse this node's helpers but launch their
    # own sequence after extra setup - set to False to suppress auto-start
    AUTO_START = True

    def __init__(self):
        super().__init__('pick_cube')

        self._action_client = ActionClient(
            self, FollowJointTrajectory,
            '/joint_trajectory_controller/follow_joint_trajectory'
        )
        self.spawn_client = self.create_client(SpawnEntity, '/spawn_entity')
        self.gripper_pub = self.create_publisher(
            Float64MultiArray, '/gripper_controller/commands', 10)
        self.weld_pub = self.create_publisher(String, '/ur_lab/grasp_weld', 10)

        self.model_states = None
        self.latest_q = None
        self.all_positions = {}
        self.create_subscription(
            ModelStates, '/model_states', self._states_cb, QoSProfile(depth=10))
        self.create_subscription(
            ModelStates, '/gazebo/model_states', self._states_cb, QoSProfile(depth=10))
        self.create_subscription(
            JointState, '/joint_states', self._joint_states_cb, QoSProfile(depth=10))

        self.get_logger().info('Waiting for trajectory controller...')
        self._action_client.wait_for_server()

        self.get_logger().info('Waiting for Gazebo services...')
        while not self.spawn_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Spawn service not ready yet...')

        if self.AUTO_START:
            threading.Thread(target=self.run_sequence, daemon=True).start()

    def _states_cb(self, msg):
        self.model_states = msg

    def _joint_states_cb(self, msg):
        for n, p in zip(msg.name, msg.position):
            self.all_positions[n] = p
        try:
            idx = [msg.name.index(j) for j in JOINTS]
            self.latest_q = [msg.position[i] for i in idx]
        except ValueError:
            pass

    def get_cube_pose(self):
        """returns measured (x, y, z) of the cube, waiting until available"""
        for _ in range(50):
            ms = self.model_states
            if ms and CUBE_NAME in ms.name:
                p = ms.pose[ms.name.index(CUBE_NAME)].position
                return p.x, p.y, p.z
            threading.Event().wait(0.1)
        return None

    def get_finger_positions(self):
        return (self.all_positions.get('finger_left_joint'),
                self.all_positions.get('finger_right_joint'))

    def get_current_q(self, timeout=5.0):
        waited = 0.0
        while self.latest_q is None and waited < timeout:
            threading.Event().wait(0.1)
            waited += 0.1
        return self.latest_q if self.latest_q is not None else list(HOME_Q)

    def move_tcp_to(self, q_seed, x, y, z, duration_steps=2, step_time=3):
        """IK to a Cartesian target and execute; returns final q or None."""
        q_target, ok = ik(q_seed, (x, y, z))
        if not ok:
            self.get_logger().error(f'IK FAILED for target ({x:.3f}, {y:.3f}, {z:.3f})')
            return None
        points = [lerp(q_seed, q_target, t / duration_steps)
                  for t in range(1, duration_steps + 1)]
        if not self.send_goal(points, step_time):
            return None
        return q_target

    # ---------- service call helper ----------
    def _call_srv(self, client, request):
        event = threading.Event()
        holder = {'resp': None}

        def done(future):
            try:
                holder['resp'] = future.result()
            except Exception as e:
                self.get_logger().error(f'{client.srv_name} call failed: {e}')
            event.set()

        client.call_async(request).add_done_callback(done)
        event.wait()
        return holder['resp']

    # ---------- gripper controller activation ----------
    def activate_gripper_controller(self):
        list_client = self.create_client(ListControllers, '/controller_manager/list_controllers')
        list_client.wait_for_service()

        resp = self._call_srv(list_client, ListControllers.Request())
        for c in (resp.controller if resp else []):
            if c.name == 'gripper_controller' and c.state == 'active':
                self.get_logger().info('gripper_controller already active')
                return

        load = self.create_client(LoadController, '/controller_manager/load_controller')
        conf = self.create_client(ConfigureController, '/controller_manager/configure_controller')
        switch = self.create_client(SwitchController, '/controller_manager/switch_controller')
        for c in (load, conf, switch):
            c.wait_for_service()

        req = LoadController.Request()
        req.name = 'gripper_controller'
        r = self._call_srv(load, req)
        if r is None or not r.ok:
            self.get_logger().warn('gripper_controller load failed (maybe already loaded)')

        req = ConfigureController.Request()
        req.name = 'gripper_controller'
        r = self._call_srv(conf, req)
        if r is None or not r.ok:
            self.get_logger().warn('gripper_controller configure failed')

        req = SwitchController.Request()
        req.activate_controllers = ['gripper_controller']
        req.strictness = SwitchController.Request.BEST_EFFORT
        req.timeout = rclpy.duration.Duration(seconds=5.0).to_msg()
        self._call_srv(switch, req)
        self.get_logger().info('gripper_controller active')

    def weld(self, command):
        """attach/detach the grasp weld via the gazebo plugin"""
        msg = String()
        msg.data = command
        self.weld_pub.publish(msg)
        threading.Event().wait(0.5)

    def set_gripper(self, command, dwell=1.0):
        """Ramp finger positions gradually - a sudden jump slams into the
        cube and ODE ejects it. Slow approach = stable pinch."""
        cur_l, cur_r = self.get_finger_positions()
        if cur_l is None:
            cur_l, cur_r = 0.0, 0.0
        steps = int(max(abs(command[0] - cur_l), abs(command[1] - cur_r)) / 0.00025)
        steps = max(2, min(steps, 80))
        for i in range(1, steps + 1):
            t = i / steps
            msg = Float64MultiArray()
            msg.data = [cur_l + (command[0] - cur_l) * t,
                        cur_r + (command[1] - cur_r) * t]
            self.gripper_pub.publish(msg)
            threading.Event().wait(0.08)
        threading.Event().wait(dwell)

    # ---------- cube spawning (high friction so fingers can hold it) ----------
    def spawn_cube(self):
        cube_sdf = f"""<?xml version="1.0" ?>
        <sdf version="1.6">
          <model name="{CUBE_NAME}">
            <static>false</static>
            <link name="link">
              <inertial>
                <mass>0.3</mass>
                <inertia><ixx>0.000125</ixx><iyy>0.000125</iyy><izz>0.000125</izz></inertia>
              </inertial>
              <collision name="collision">
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
                <surface>
                  <friction><ode><mu>100</mu><mu2>100</mu2></ode></friction>
                  <contact><ode><max_vel>0.05</max_vel><min_depth>0.0005</min_depth></ode></contact>
                </surface>
              </collision>
              <visual name="visual">
                <geometry><box><size>0.05 0.05 0.05</size></box></geometry>
                <material>
                  <ambient>1 0 0 1</ambient>
                  <diffuse>1 0 0 1</diffuse>
                </material>
              </visual>
            </link>
          </model>
        </sdf>
        """
        req = SpawnEntity.Request()
        req.name = CUBE_NAME
        req.xml = cube_sdf
        req.reference_frame = 'world'
        req.initial_pose.position.x = CUBE_X
        req.initial_pose.position.y = CUBE_Y
        req.initial_pose.position.z = CUBE_Z
        req.initial_pose.orientation.w = 1.0

        event = threading.Event()

        def done(future):
            try:
                res = future.result()
                if res.success:
                    self.get_logger().info(f'{CUBE_NAME} spawned')
                else:
                    self.get_logger().error(f'Spawn failed: {res.status_message}')
            except Exception as e:
                self.get_logger().error(f'Spawn service call failed: {e}')
            event.set()

        self.spawn_client.call_async(req).add_done_callback(done)
        event.wait()
        threading.Event().wait(1.5)

    # ---------- arm motion ----------
    def send_goal(self, points, starttime=4):
        goal_msg = FollowJointTrajectory.Goal()
        goal_msg.trajectory.joint_names = JOINTS

        tt = starttime
        for i in points:
            p = JointTrajectoryPoint()
            p.positions = i
            p.time_from_start.sec = tt
            p.velocities = [0.0] * 6
            tt += 3
            goal_msg.trajectory.points.append(p)

        move_event = threading.Event()
        result_status = {'success': False}

        def goal_response_callback(future):
            goal_handle = future.result()
            if not goal_handle.accepted:
                self.get_logger().error('Goal rejected by controller')
                move_event.set()
                return
            result_future = goal_handle.get_result_async()

            def result_callback(future_res):
                result = future_res.result().result
                if result.error_code != 0:
                    self.get_logger().error(f'Trajectory error code: {result.error_code}')
                else:
                    result_status['success'] = True
                move_event.set()

            result_future.add_done_callback(result_callback)

        self._action_client.send_goal_async(goal_msg).add_done_callback(goal_response_callback)
        move_event.wait()
        return result_status['success']

    # ---------- sequence ----------
    def run_sequence(self):
        self.get_logger().info("--- Pick sequence started ---")

        self.activate_gripper_controller()
        self.set_gripper(GRIP_OPEN)
        self.weld(f'detach {CUBE_NAME}')   # make sure nothing is welded from a previous run
        self.spawn_cube()

        cube = self.get_cube_pose()
        if cube is None:
            self.get_logger().error(f'{CUBE_NAME} not found in model_states')
            return
        cx, cy, cube_z = cube
        # aim at where the cube ACTUALLY rests (it may bounce when dropped)
        self.get_logger().info(
            f'Cube settled at x={cx:.3f}, y={cy:.3f}, z={cube_z:.3f}')

        grasp_z = cube_z + GRASP_TOOL_Z_OFFSET

        # Step 1: home (known-safe joint pose)
        self.get_logger().info('Step 1: home...')
        self.send_goal([HOME_Q])
        q = self.get_current_q()

        # Step 2: hover above cube
        self.get_logger().info(f'Step 2: hover above cube ({cx}, {cy}, {grasp_z + 0.075:.3f})...')
        q = self.move_tcp_to(q, cx, cy, grasp_z + 0.075, duration_steps=3, step_time=3)
        if q is None:
            return

        # Step 3: descend to grasp height (fingers straddle the cube center)
        self.get_logger().info(f'Step 3: descend to {grasp_z:.3f}...')
        q = self.move_tcp_to(q, cx, cy, grasp_z, duration_steps=3, step_time=2)
        if q is None:
            return

        # where did the arm REALLY end up? (goal tolerance is not zero)
        T = fk(self.get_current_q())
        real = FLIP @ T[:3, 3]
        self.get_logger().info(
            f'  achieved TCP=({real[0]:.4f}, {real[1]:.4f}, {real[2]:.4f}) '
            f'target=({cx:.4f}, {cy:.4f}, {grasp_z:.4f})')
        threading.Event().wait(1.0)   # let micro-vibrations die out

        # pre-close sanity: cube must still be under the gripper
        check = self.get_cube_pose()
        if check is None or abs(check[0] - cx) > 0.03 or abs(check[1] - cy) > 0.03:
            where = f'({check[0]:.3f}, {check[1]:.3f})' if check else 'gone'
            self.get_logger().error(
                f'Cube not under gripper anymore ({where}). Aborting.')
            return

        # Lock the cube to the gripper BEFORE closing - otherwise the first
        # finger to make contact shoves the cube away (ODE impulse).
        self.get_logger().info('Step 4: locking cube to gripper...')
        self.weld(f'attach {CUBE_NAME}')

        self.set_gripper(GRIP_CLOSED, dwell=SETTLE_BEFORE_LIFT)
        fl2, fr2 = self.get_finger_positions()
        self.get_logger().info(
            f'  fingers closed to {fl2:.4f}/{fr2:.4f} (grasp locked)')

        # Step 5: lift until cube reaches TARGET_CUBE_Z
        self.get_logger().info(f'Step 5: lifting until cube z >= {TARGET_CUBE_Z} ...')
        lifted = False
        cz = cube_z
        for step in range(MAX_LIFT_STEPS):
            z_next = grasp_z + LIFT_STEP * (step + 1)
            q_new = self.move_tcp_to(q, cx, cy, z_next, duration_steps=1, step_time=3)
            if q_new is None:
                break
            q = q_new
            pose = self.get_cube_pose()
            cz = pose[2] if pose else None
            self.get_logger().info(f'  lift {step + 1}: tool z={z_next:.3f}, cube z={cz}')
            if cz is not None and cz >= TARGET_CUBE_Z:
                lifted = True
                break

        if lifted:
            self.get_logger().info(
                f'--- SUCCESS: cube held at z={cz:.3f}, stopped at target height ---')
        else:
            self.get_logger().warn(
                '--- Lift ended before reaching target height '
                '(cube may have slipped: raise GRIP_CLOSED or check alignment) ---')

        self.get_logger().info("Holding position. Ctrl+C to exit.")


def main(args=None):
    rclpy.init(args=args)
    node = PickCube()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
