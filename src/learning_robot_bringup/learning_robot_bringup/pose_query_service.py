import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

from learning_robot_interfaces.srv import QueryObjectPose


class PoseQueryService(Node):
    """
    Day 2：根据 object_id 返回一个模拟物体位姿。

    当前位姿是人为设定的“仿真真值”。
    第 6 周会由相机、点云和 TF 变换提供真实或仿真的物体位姿。
    """

    def __init__(self):
        super().__init__('pose_query_service')

        self.object_positions = {
            'demo_cube': (0.45, 0.00, 0.15),
            'demo_cylinder': (0.35, -0.20, 0.20),
        }

        self.service = self.create_service(
            QueryObjectPose,
            '/query_object_pose',
            self.handle_query_object_pose,
        )

        self.get_logger().info(
            'pose_query_service started: waiting for /query_object_pose requests.'
        )

    def make_pose(self, x, y, z):
        pose = PoseStamped()

        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = 'base_link'

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        # 当前先使用单位四元数：不旋转。
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = 0.0
        pose.pose.orientation.w = 1.0

        return pose

    def handle_query_object_pose(self, request, response):
        object_id = request.object_id.strip()
        position = self.object_positions.get(object_id)

        if position is None:
            response.success = False
            response.message = (
                f"UNKNOWN_OBJECT: '{object_id}'. "
                f"Available objects: {', '.join(self.object_positions.keys())}."
            )
            response.pose = self.make_pose(0.0, 0.0, 0.0)

            self.get_logger().warning(response.message)
            return response

        response.pose = self.make_pose(*position)
        response.success = True
        response.message = f"OK: pose returned for '{object_id}'."

        self.get_logger().info(
            f"Returned pose for '{object_id}': "
            f"x={position[0]:.3f}, y={position[1]:.3f}, z={position[2]:.3f}"
        )

        return response


def main(args=None):
    rclpy.init(args=args)
    node = PoseQueryService()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()