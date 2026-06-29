import rclpy
from rclpy.node import Node


class HealthCheck(Node):
    """
    Day 1 健康检查节点。

    用于验证：
    1. ROS2 Python 节点可以正常运行；
    2. 定时器 callback 可以持续执行；
    3. 后续 ros2 run 能找到这个节点入口。
    """

    def __init__(self):
        super().__init__('health_check')

        self.heartbeat_count = 0

        # 每 2 秒调用一次 on_timer()
        self.timer = self.create_timer(2.0, self.on_timer)

        self.get_logger().info(
            'health_check started: ROS2 workspace and Python entry point are working.'
        )

    def on_timer(self):
        self.heartbeat_count += 1

        self.get_logger().info(
            f'heartbeat={self.heartbeat_count}: '
            'learning_robot_bringup is alive.'
        )


def main(args=None):
    rclpy.init(args=args)

    node = HealthCheck()

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
