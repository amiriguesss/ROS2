#!/usr/bin/env python3
"""
scan_pick: colour-sorting pick demo for the UR5e + 2-finger gripper.

Three 0.05 m cubes (red, blue, yellow) are spawned in a single line along
+X on the table (constant y, constant z, different x, colours shuffled on
every run). A camera mounted on the gripper looks straight down at the
table. The arm sweeps along the cube line, stopping at fixed x intervals;
at every stop the centre of the camera image is classified by mean RGB
dominance. As soon as the RED cube is seen the sweep stops and the exact
same grasp routine as pick_cube runs on that cube:

    hover -> descend -> weld -> close fingers -> lift to TARGET_CUBE_Z

Blue and yellow cubes are simply passed over.

Run with:  ros2 run ur_lab scan_pick
(requires the sim with the wrist camera: rebuild + relaunch sim.launch.py)
"""

import random
import threading
from collections import Counter, deque

import rclpy
from rclpy.qos import qos_profile_sensor_data

from gazebo_msgs.srv import DeleteEntity, SpawnEntity
from sensor_msgs.msg import Image

from .pick_cube import (
    PickCube,
    HOME_Q,
    GRIP_OPEN,
    GRIP_CLOSED,
    GRASP_TOOL_Z_OFFSET,
    TARGET_CUBE_Z,
    LIFT_STEP,
    MAX_LIFT_STEPS,
    SETTLE_BEFORE_LIFT,
)

# ================== TUNING CONSTANTS ==================
CUBE_NAMES = {
    'red': 'scan_cube_red',
    'blue': 'scan_cube_blue',
    'yellow': 'scan_cube_yellow',
}
COLOR_RGBA = {
    'red': '1 0 0 1',
    'blue': '0 0 1 1',
    'yellow': '1 1 0 1',
}
CUBE_XS = [0.58, 0.68, 0.78]   # the three line positions along x
# (x >= 0.80 is beyond the UR5e reach at scan height!)
SCAN_Y = 0.0                   # constant y of the line
SCAN_Z_SPAWN = 0.4             # spawn height (cubes drop onto the table)
SCAN_SETTLE_TIME = 2.5         # seconds to let the dropped cubes come to rest
SCAN_HOVER_ABOVE_CUBE = 0.12   # TCP height above the resting cubes while
                               # scanning (lower hover = cube fills the image)
SCAN_X_START = 0.53            # sweep starts slightly before the first cube
SCAN_X_END = 0.79              # sweep ends just past the last cube (reach limit)
SCAN_STEP = 0.02               # x advance per scan stop (small stops = several
                               # classification chances directly over each cube)
SCAN_DWELL = 1.5               # seconds spent classifying at every stop
TARGET_COLOR = 'red'           # the colour we pick up

IMG_TOPIC = '/wrist_camera/image_raw'
CROP = 3          # classify the mean colour of the centre 1/CROP of the image
MIN_VAL = 60      # minimum mean channel value for any colour to count
DOMINANCE = 1.6   # dominant channels must exceed this ratio over the others
WHOLE_IMG_MIN_FRAC = 0.01    # fallback - min fraction of coloured pixels


def classify_rgb(r, g, b):
    """very robust mean-colour classifier for the saturated cube materials"""
    if max(r, g, b) < MIN_VAL:
        return 'none'
    if r > DOMINANCE * g and r > DOMINANCE * b:
        return 'red'
    if b > DOMINANCE * r and b > DOMINANCE * g:
        return 'blue'
    if r > DOMINANCE * b and g > DOMINANCE * b:
        return 'yellow'
    return 'none'


class ScanPick(PickCube):
    """sweeps the wrist camera across the cube line and picks the red cube"""

    # PickCube.__init__ would otherwise launch its own pick sequence before
    # we get a chance to subscribe to the camera - we start it ourselves
    AUTO_START = False

    def __init__(self):
        super().__init__()   # arm/gripper/weld/model-state plumbing

        self._label_buf = deque(maxlen=12)
        self._first_image = threading.Event()
        # sensor-data QoS: best-effort subscriber is compatible with both
        # reliable and best-effort camera publishers
        self.create_subscription(
            Image, IMG_TOPIC, self._image_cb, qos_profile_sensor_data)
        self.delete_client = self.create_client(DeleteEntity, '/delete_entity')

        self.get_logger().info(f'Waiting for wrist camera on {IMG_TOPIC} ...')
        if not self._first_image.wait(15.0):
            self.get_logger().warn(
                'No camera images yet - colour detection may not work. '
                'Did you rebuild ur_lab and relaunch the sim?')
        else:
            self.get_logger().info('Wrist camera is streaming')

        threading.Thread(target=self.run_sequence, daemon=True).start()

    # ---------- camera ----------
    def _image_cb(self, msg):
        self._first_image.set()
        label, rgb, info = self._classify(msg)
        self._label_buf.append((label, rgb, info))
        self.get_logger().debug(f'camera: rgb={rgb} -> {label} ({info})')

    def _classify(self, msg):
        """classify one camera frame.

        Primary signal - mean colour of the centre crop (the cube fills it
        when we are stopped on top of it). Fallback - a whole-image scan for
        saturated colour pixels with a centroid gate, so a slightly off aim
        still finds a cube that is visible but not dead-centre.
        Returns (label, (r, g, b), info).
        """
        h, w = msg.height, msg.width
        data, step = msg.data, msg.step
        swap_rb = 'bgr' in msg.encoding

        # --- primary - centre crop mean ---
        r0, r1 = h // CROP, (2 * h) // CROP
        c0, c1 = w // CROP, (2 * w) // CROP
        n = (r1 - r0) * (c1 - c0)
        sums = [0, 0, 0]
        for row in range(r0, r1):
            base = row * step
            for col in range(c0, c1):
                px = base + col * 3
                sums[0] += data[px]
                sums[1] += data[px + 1]
                sums[2] += data[px + 2]
        r, g, b = (s / n for s in sums)
        if swap_rb:
            r, b = b, r
        label = classify_rgb(r, g, b)
        if label != 'none':
            return label, (r, g, b), 'centre-crop mean'

        # --- fallback - whole-image colour scan (subsampled) ---
        counts = {'red': 0, 'blue': 0, 'yellow': 0}
        sums_xy = {'red': [0, 0], 'blue': [0, 0], 'yellow': [0, 0]}
        total = 0
        for row in range(0, h, 4):
            base = row * step
            for col in range(0, w, 4):
                total += 1
                px = base + col * 3
                pr, pg, pb = data[px], data[px + 1], data[px + 2]
                if swap_rb:
                    pr, pb = pb, pr
                lab = classify_rgb(pr, pg, pb)
                if lab in counts:
                    counts[lab] += 1
                    sums_xy[lab][0] += col
                    sums_xy[lab][1] += row
        if not total:
            return 'none', (r, g, b), 'empty frame'
        best = max(counts, key=counts.get)
        frac = counts[best] / total
        if frac >= WHOLE_IMG_MIN_FRAC:
            cx = sums_xy[best][0] / counts[best] / w
            cy = sums_xy[best][1] / counts[best] / h
            if 0.15 < cx < 0.85 and 0.15 < cy < 0.85:
                return best, (r, g, b), (
                    f'whole-image {best} {frac * 100:.1f}% at '
                    f'({cx:.2f}, {cy:.2f})')
            return 'none', (r, g, b), (
                f'{best} {frac * 100:.1f}% but at image edge '
                f'({cx:.2f}, {cy:.2f})')
        return 'none', (r, g, b), f'no colour > {WHOLE_IMG_MIN_FRAC:.0%}'

    def classify_at_stop(self):
        """collect frames for SCAN_DWELL seconds, log diagnostics and
        return the majority label"""
        self._label_buf.clear()
        threading.Event().wait(SCAN_DWELL)
        if not self._label_buf:
            self.get_logger().warn(
                '  no camera frames received at this stop!')
            return 'none'
        rgb = tuple(
            sum(f[1][i] for f in self._label_buf) / len(self._label_buf)
            for i in range(3))
        label = Counter(f[0] for f in self._label_buf).most_common(1)[0][0]
        info = self._label_buf[-1][2]
        self.get_logger().info(
            f'  camera mean rgb=({rgb[0]:.0f}, {rgb[1]:.0f}, {rgb[2]:.0f}) '
            f'-> {label!r} ({len(self._label_buf)} frames, {info})')
        return label

    # ---------- cubes ----------
    def _model_pose(self, name, wait=2.0):
        """returns measured (x, y, z) of a model, waiting until available"""
        for _ in range(int(wait / 0.1)):
            ms = self.model_states
            if ms and name in ms.name:
                p = ms.pose[ms.name.index(name)].position
                return p.x, p.y, p.z
            threading.Event().wait(0.1)
        return None

    def _delete_if_exists(self, name):
        """clean up leftovers from a previous run"""
        req = DeleteEntity.Request()
        req.name = name
        resp = self._call_srv(self.delete_client, req)
        if resp is not None and resp.success:
            self.get_logger().info(f'deleted leftover model {name}')

    def _spawn_cube(self, name, x, y, z, color_rgba):
        cube_sdf = f"""<?xml version="1.0" ?>
        <sdf version="1.6">
          <model name="{name}">
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

        def done(future):
            try:
                res = future.result()
                if res.success:
                    self.get_logger().info(f'{name} spawned')
                else:
                    self.get_logger().error(f'Spawn failed: {res.status_message}')
            except Exception as e:
                self.get_logger().error(f'Spawn service call failed: {e}')
            event.set()

        self.spawn_client.call_async(req).add_done_callback(done)
        event.wait()
        threading.Event().wait(0.5)

    def spawn_three_cubes(self):
        """spawn the three cubes in a line; colours are shuffled every run"""
        items = list(CUBE_NAMES.items())
        random.shuffle(items)
        for (color, name), x in zip(items, CUBE_XS):
            self._delete_if_exists(name)
            self._spawn_cube(name, x, SCAN_Y, SCAN_Z_SPAWN, COLOR_RGBA[color])
        self.get_logger().info(
            'Cubes spawned in a line (colours shuffled - only the camera '
            'knows where the red one is)')

    # ---------- sequence ----------
    def run_sequence(self):
        self.get_logger().info('--- Scan & pick sequence started ---')

        self.activate_gripper_controller()
        self.set_gripper(GRIP_OPEN)
        for name in CUBE_NAMES.values():
            self.weld(f'detach {name}')

        self.spawn_three_cubes()
        threading.Event().wait(SCAN_SETTLE_TIME)

        # where did the cubes actually come to rest? (they drop, then settle)
        rest_z = None
        for color, name in CUBE_NAMES.items():
            pose = self._model_pose(name)
            if pose is None:
                self.get_logger().error(f'{name} not found in model_states')
                return
            self.get_logger().info(
                f'{color} cube rests at x={pose[0]:.3f}, y={pose[1]:.3f}, '
                f'z={pose[2]:.3f}')
            rest_z = pose[2] if rest_z is None else max(rest_z, pose[2])
        scan_z = rest_z + SCAN_HOVER_ABOVE_CUBE
        self.get_logger().info(f'Scan height: TCP z = {scan_z:.3f}')

        # Step 1: home (known-safe joint pose)
        self.get_logger().info('Step 1: home...')
        self.send_goal([HOME_Q])
        q = self.get_current_q()

        # Step 2: hover above the start of the line
        self.get_logger().info(
            f'Step 2: hover at scan start ({SCAN_X_START}, {SCAN_Y}, '
            f'{scan_z:.3f})...')
        q = self.move_tcp_to(q, SCAN_X_START, SCAN_Y, scan_z,
                             duration_steps=3, step_time=3)
        if q is None:
            return

        # Step 3: sweep along the line, classifying colours at every stop
        self.get_logger().info(
            f'Step 3: sweeping x = {SCAN_X_START} .. {SCAN_X_END} while the '
            f'camera looks for the {TARGET_COLOR} cube...')
        trail = []
        found = False
        n_steps = int(round((SCAN_X_END - SCAN_X_START) / SCAN_STEP))
        for i in range(n_steps + 1):
            x = SCAN_X_START + i * SCAN_STEP
            if i > 0:
                q_new = self.move_tcp_to(q, x, SCAN_Y, scan_z,
                                         duration_steps=1, step_time=2)
                if q_new is None:
                    self.get_logger().warn(
                        'Move failed - classifying from the current pose')
                else:
                    q = q_new
            label = self.classify_at_stop()
            trail.append((round(x, 2), label))
            self.get_logger().info(f'  scan x={x:.2f}: camera sees {label!r}')
            if label == TARGET_COLOR:
                found = True
                break

        if not found:
            self.get_logger().error(
                f'No {TARGET_COLOR} cube detected during the sweep {trail}. '
                'Aborting.')
            return

        # Step 4: grasp the red cube (same routine as pick_cube)
        self.get_logger().info(
            f'Step 4: {TARGET_COLOR} cube spotted! Switching to grasp...')
        cube = self._model_pose(CUBE_NAMES[TARGET_COLOR])
        if cube is None:
            self.get_logger().error(f'{CUBE_NAMES[TARGET_COLOR]} vanished')
            return
        cx, cy, cube_z = cube
        grasp_z = cube_z + GRASP_TOOL_Z_OFFSET
        self.get_logger().info(
            f'  target rests at ({cx:.3f}, {cy:.3f}, {cube_z:.3f})')

        self.get_logger().info(
            f'  hovering above target ({cx:.3f}, {cy:.3f}, '
            f'{grasp_z + 0.075:.3f})...')
        q = self.move_tcp_to(q, cx, cy, grasp_z + 0.075,
                             duration_steps=3, step_time=3)
        if q is None:
            return

        self.get_logger().info(f'  descending to {grasp_z:.3f}...')
        q = self.move_tcp_to(q, cx, cy, grasp_z, duration_steps=3, step_time=2)
        if q is None:
            return
        threading.Event().wait(1.0)

        # pre-close sanity: cube must still be under the gripper
        check = self._model_pose(CUBE_NAMES[TARGET_COLOR])
        if check is None or abs(check[0] - cx) > 0.03 or abs(check[1] - cy) > 0.03:
            where = f'({check[0]:.3f}, {check[1]:.3f})' if check else 'gone'
            self.get_logger().error(
                f'Cube not under gripper anymore ({where}). Aborting.')
            return

        self.get_logger().info('  locking cube to gripper...')
        self.weld(f'attach {CUBE_NAMES[TARGET_COLOR]}')
        self.set_gripper(GRIP_CLOSED, dwell=SETTLE_BEFORE_LIFT)

        # Step 5: lift until the cube reaches TARGET_CUBE_Z
        self.get_logger().info(
            f'Step 5: lifting until cube z >= {TARGET_CUBE_Z} ...')
        lifted = False
        cz = cube_z
        for step in range(MAX_LIFT_STEPS):
            z_next = grasp_z + LIFT_STEP * (step + 1)
            q_new = self.move_tcp_to(q, cx, cy, z_next,
                                     duration_steps=1, step_time=3)
            if q_new is None:
                break
            q = q_new
            pose = self._model_pose(CUBE_NAMES[TARGET_COLOR])
            cz = pose[2] if pose else None
            self.get_logger().info(
                f'  lift {step + 1}: tool z={z_next:.3f}, cube z={cz}')
            if cz is not None and cz >= TARGET_CUBE_Z:
                lifted = True
                break

        if lifted:
            self.get_logger().info(
                f'--- SUCCESS: {TARGET_COLOR} cube held at z={cz:.3f} ---')
        else:
            self.get_logger().warn(
                '--- Lift ended before reaching target height '
                '(cube may have slipped) ---')
        self.get_logger().info('Holding position. Ctrl+C to exit.')


def main(args=None):
    rclpy.init(args=args)
    node = ScanPick()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
