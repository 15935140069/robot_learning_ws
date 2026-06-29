import rclpy
from rclpy.node import Node

from geometry_msgs.msg import PoseStamped

from learning_robot_interfaces.srv import QueryObjectPose


class PoseQueryService(Node):
    """
    Day 3：由 YAML 参数提供物体初始位姿的查询服务。

    后续第 6 周会由视觉、点云与 TF 变换提供真实物体位姿。
    当前仅用 YAML 中的场景真值模拟查询结果。
    """

    def __init__(self):
        super().__init__('pose_query_service')

        self.declare_parameter('frame_id', 'base_link')
        self.declare_parameter(
            'demo_cube_position_xyz',
            [0.45, 0.0, 0.15],
        )
        self.declare_parameter(
            'demo_cylinder_position_xyz',
            [0.35, -0.20, 0.20],
        )
        self.declare_parameter('debug', False)

        self.frame_id = str(
            self.get_parameter('frame_id').value
        )
        self.debug = bool(
            self.get_parameter('debug').value
        )

        demo_cube_position = self.read_position_parameter(
            'demo_cube_position_xyz'
        )
        demo_cylinder_position = self.read_position_parameter(
            'demo_cylinder_position_xyz'
        )

        self.object_positions = {
            'demo_cube': demo_cube_position,
            'demo_cylinder': demo_cylinder_position,
        }

        self.service = self.create_service(
            QueryObjectPose,
            'query_object_pose',
            self.handle_query_object_pose,
        )

        self.get_logger().info(
            'pose_query_service started with '
            f'frame_id={self.frame_id}, debug={self.debug}.'
        )

        if self.debug:
            self.get_logger().info(
                f'Configured object positions: {self.object_positions}'
            )

    def read_position_parameter(self, parameter_name):
        values = list(
            self.get_parameter(parameter_name).value
        )

        if len(values) != 3:
            raise ValueError(
                f'{parameter_name} must contain exactly '
                f'3 values: [x, y, z].'
            )

        return tuple(float(value) for value in values)

    def make_pose(self, x, y, z):
        pose = PoseStamped()

        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = self.frame_id

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

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
                f"Available objects: "
                f"{', '.join(self.object_positions.keys())}."
            )
            response.pose = self.make_pose(0.0, 0.0, 0.0)

            self.get_logger().warning(response.message)
            return response

        response.pose = self.make_pose(*position)
        response.success = True
        response.message = f"OK: pose returned for '{object_id}'."

        if self.debug:
            self.get_logger().info(
                f"Returned pose for '{object_id}': "
                f'x={position[0]:.3f}, '
                f'y={position[1]:.3f}, '
                f'z={position[2]:.3f}'
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