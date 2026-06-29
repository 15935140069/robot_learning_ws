import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


class JointStateMockPublisher(Node):
    """
    Day 3：通过 ROS2 参数配置的模拟关节状态发布节点。

    参数由 normal.yaml 或 debug.yaml 提供。
    后续 robot_state_publisher、RViz、MoveIt2 都会订阅 joint_states。
    """

    def __init__(self):
        super().__init__('joint_state_mock_publisher')

        self.declare_parameter('publish_rate_hz', 10.0)
        self.declare_parameter('motion_amplitude_rad', 0.5)
        self.declare_parameter('frame_id', 'base_link')
        self.declare_parameter('debug', False)
        self.declare_parameter(
            'joint_names',
            [
                'joint_1',
                'joint_2',
                'joint_3',
                'joint_4',
                'joint_5',
                'joint_6',
            ],
        )
        self.declare_parameter(
            'joint_phase_offsets_rad',
            [0.0, 0.5, 1.0, 1.5, 2.0, 2.5],
        )

        self.publish_rate_hz = float(
            self.get_parameter('publish_rate_hz').value
        )
        self.motion_amplitude_rad = float(
            self.get_parameter('motion_amplitude_rad').value
        )
        self.frame_id = str(
            self.get_parameter('frame_id').value
        )
        self.debug = bool(
            self.get_parameter('debug').value
        )
        self.joint_names = list(
            self.get_parameter('joint_names').value
        )
        self.joint_phase_offsets_rad = [
            float(value)
            for value in self.get_parameter(
                'joint_phase_offsets_rad'
            ).value
        ]

        if self.publish_rate_hz <= 0.0:
            raise ValueError('publish_rate_hz must be greater than 0.')

        if len(self.joint_names) != len(self.joint_phase_offsets_rad):
            raise ValueError(
                'joint_names and joint_phase_offsets_rad '
                'must have the same length.'
            )

        self.publisher = self.create_publisher(
            JointState,
            'joint_states',
            10,
        )

        self.publish_count = 0
        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz,
            self.publish_joint_state,
        )

        self.get_logger().info(
            'joint_state_mock_publisher started with '
            f'publish_rate_hz={self.publish_rate_hz}, '
            f'motion_amplitude_rad={self.motion_amplitude_rad}, '
            f'frame_id={self.frame_id}, '
            f'debug={self.debug}.'
        )

    def publish_joint_state(self):
        now = self.get_clock().now()
        t_seconds = now.nanoseconds / 1_000_000_000.0

        message = JointState()
        message.header.stamp = now.to_msg()
        message.header.frame_id = self.frame_id
        message.name = list(self.joint_names)

        message.position = [
            self.motion_amplitude_rad * math.sin(
                t_seconds + phase
            )
            for phase in self.joint_phase_offsets_rad
        ]

        message.velocity = [
            self.motion_amplitude_rad * math.cos(
                t_seconds + phase
            )
            for phase in self.joint_phase_offsets_rad
        ]

        self.publisher.publish(message)
        self.publish_count += 1

        log_every_n_messages = max(
            1,
            round(self.publish_rate_hz),
        )

        if self.debug and (
            self.publish_count % log_every_n_messages == 0
        ):
            self.get_logger().info(
                f'Published joint_states, count={self.publish_count}'
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