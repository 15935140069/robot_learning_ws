import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

class JointStateMockPublisher(Node):
    """
    Day 2：以固定频率发布模拟机械臂关节状态。

    后续 robot_state_publisher、RViz、MoveIt2 都会订阅 /joint_states。
    """

    def __init__(self):
        super().__init__('joint_state_mock_publisher')

        self.publisher = self.create_publisher(
            JointState,
            '/joint_states',
            10,
        )

        self.joint_names = [
            'joint_1',
            'joint_2',
            'joint_3',
            'joint_4',
            'joint_5',
            'joint_6',
        ]

        self.phases = [
            0.0,
            0.5,
            1.0,
            1.5,
            2.0,
            2.5,
        ]

        # 10 Hz：每 0.1 秒发布一次
        self.timer = self.create_timer(0.1, self.publish_joint_state)
        self.publish_count = 0

        self.get_logger().info(
            'joint_state_mock_publisher started: publishing /joint_states at 10 Hz.'
        )

    def publish_joint_state(self):
        now = self.get_clock().now()
        t_seconds = now.nanoseconds / 1_000_000_000.0

        message = JointState()
        message.header.stamp = now.to_msg()
        message.name = list(self.joint_names)

        # 用正弦曲线模拟 6 个关节持续运动，单位是弧度 / 弧度每秒
        message.position = [
            0.5 * math.sin(t_seconds + phase)
            for phase in self.phases
        ]

        message.velocity = [
            0.5 * math.cos(t_seconds + phase)
            for phase in self.phases
        ]

        self.publisher.publish(message)

        self.publish_count += 1

        # 每秒打印一次，避免 10 Hz 日志刷屏
        if self.publish_count % 10 == 0:
            self.get_logger().info(
                f'Published /joint_states, count={self.publish_count}'
            )


def main(args=None):
    rclpy.init(args=args)
    node = JointStateMockPublisher()

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