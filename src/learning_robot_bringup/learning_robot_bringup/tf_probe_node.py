"""Day 4：验证相机坐标点到机械臂基座坐标的 TF 变换。"""

import time

import rclpy
from geometry_msgs.msg import PointStamped
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from tf2_geometry_msgs import do_transform_point
from tf2_ros import Buffer, TransformException, TransformListener


class TfProbeNode(Node):
    """将一个相机坐标系中的已知点变换到 base_link。"""

    def __init__(self):
        super().__init__('tf_probe_node')

        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter(
            'source_frame',
            'camera_optical_frame',
        )
        self.declare_parameter('point_xyz', [0.0, 0.0, 1.0])
        self.declare_parameter(
            'expected_base_xyz',
            [0.164, -0.072, 0.227],
        )
        self.declare_parameter('tolerance_m', 0.002)

        self.target_frame = str(
            self.get_parameter('target_frame').value
        )
        self.source_frame = str(
            self.get_parameter('source_frame').value
        )
        self.point_xyz = self.read_xyz('point_xyz')
        self.expected_base_xyz = self.read_xyz(
            'expected_base_xyz'
        )
        self.tolerance_m = float(
            self.get_parameter('tolerance_m').value
        )

        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(
            self.tf_buffer,
            self,
        )

    def read_xyz(self, parameter_name):
        """读取并检查 XYZ 三维坐标参数。"""
        values = list(
            self.get_parameter(parameter_name).value
        )

        if len(values) != 3:
            raise ValueError(
                f'{parameter_name} 必须包含 3 个数值：[x, y, z]。'
            )

        return tuple(float(value) for value in values)

    @staticmethod
    def format_xyz(values):
        """把 XYZ 坐标格式化为便于阅读的文字。"""
        return (
            f'[{values[0]:.6f}, '
            f'{values[1]:.6f}, '
            f'{values[2]:.6f}]'
        )

    def run_probe(self):
        """等待 TF 就绪，执行一次点变换，并输出误差。"""
        source_point = PointStamped()
        source_point.header.frame_id = self.source_frame
        source_point.point.x = self.point_xyz[0]
        source_point.point.y = self.point_xyz[1]
        source_point.point.z = self.point_xyz[2]

        deadline = time.monotonic() + 5.0
        transform = None

        self.get_logger().info(
            f'等待 TF：{self.target_frame} <- {self.source_frame}'
        )
        self.get_logger().info(
            f'相机坐标系输入点：{self.format_xyz(self.point_xyz)} m'
        )

        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)

            try:
                transform = self.tf_buffer.lookup_transform(
                    self.target_frame,
                    self.source_frame,
                    Time(),
                    timeout=Duration(seconds=0.0),
                )
                break
            except TransformException:
                continue

        if transform is None:
            self.get_logger().error(
                '失败：5 秒内没有等到所需 TF 变换。'
            )
            return 2

        output_point = do_transform_point(
            source_point,
            transform,
        )

        actual_xyz = (
            output_point.point.x,
            output_point.point.y,
            output_point.point.z,
        )

        errors = [
            abs(actual - expected)
            for actual, expected in zip(
                actual_xyz,
                self.expected_base_xyz,
            )
        ]
        max_error = max(errors)

        self.get_logger().info(
            f'base_link 输出点：{self.format_xyz(actual_xyz)} m'
        )
        self.get_logger().info(
            '手算参考点：'
            f'{self.format_xyz(self.expected_base_xyz)} m'
        )
        self.get_logger().info(
            f'最大绝对误差：{max_error:.6f} m'
        )

        if max_error <= self.tolerance_m:
            self.get_logger().info(
                '结果：通过。TF 计算结果与手算参考值一致。'
            )
            return 0

        self.get_logger().error(
            '结果：失败。TF 计算结果与手算参考值差异过大。'
        )
        return 1


def main(args=None):
    """运行一次 TF 坐标变换验证后退出。"""
    rclpy.init(args=args)
    node = TfProbeNode()
    exit_code = 1

    try:
        exit_code = node.run_probe()
    except KeyboardInterrupt:
        exit_code = 130
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())