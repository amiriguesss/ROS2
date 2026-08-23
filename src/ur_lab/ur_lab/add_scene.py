import rclpy
from rclpy.node import Node

from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose


class AddScene(Node):

    def __init__(self):
        super().__init__('add_scene')

        self.publisher = self.create_publisher(
            PlanningScene,
            '/planning_scene',
            10
        )

        self.timer = self.create_timer(2.0, self.add_objects)

    def add_objects(self):

        scene = PlanningScene()
        scene.is_diff = True

        objects = []

        # -------- TABLE --------
        table = CollisionObject()
        table.id = "table"
        table.header.frame_id = "world"

        primitive = SolidPrimitive()
        primitive.type = SolidPrimitive.BOX
        primitive.dimensions = [0.8, 1.2, 0.6]

        pose = Pose()
        pose.position.x = 0.8
        pose.position.y = 0.0
        pose.position.z = 0.0
        pose.orientation.w = 1.0

        table.primitives.append(primitive)
        table.primitive_poses.append(pose)
        table.operation = CollisionObject.ADD

        objects.append(table)

        # -------- RED CUBE --------
        red_cube = CollisionObject()
        red_cube.id = "red_cube"
        red_cube.header.frame_id = "world"

        cube = SolidPrimitive()
        cube.type = SolidPrimitive.BOX
        cube.dimensions = [0.05, 0.05, 0.05]

        pose = Pose()
        pose.position.x = 0.8
        pose.position.y = 0.15
        pose.position.z = 0.3
        pose.orientation.w = 1.0

        red_cube.primitives.append(cube)
        red_cube.primitive_poses.append(pose)
        red_cube.operation = CollisionObject.ADD

        objects.append(red_cube)

        # -------- BLUE CUBE --------
        blue_cube = CollisionObject()
        blue_cube.id = "blue_cube"
        blue_cube.header.frame_id = "world"

        cube = SolidPrimitive()
        cube.type = SolidPrimitive.BOX
        cube.dimensions = [0.05, 0.05, 0.05]

        pose = Pose()
        pose.position.x = 0.8
        pose.position.y = -0.15
        pose.position.z = 0.3
        pose.orientation.w = 1.0

        blue_cube.primitives.append(cube)
        blue_cube.primitive_poses.append(pose)
        blue_cube.operation = CollisionObject.ADD

        objects.append(blue_cube)

        scene.world.collision_objects = objects

        self.publisher.publish(scene)

        self.get_logger().info("Objects added to planning scene")
        self.timer.cancel()


def main():
    rclpy.init()
    node = AddScene()
    rclpy.spin(node)


if __name__ == '__main__':
    main()

