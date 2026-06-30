from time import monotonic

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from sensor_msgs.msg import JointState

from learning_robot_interfaces.action import ExecutePick
from learning_robot_interfaces.srv import QueryObjectPose


class PickTaskClient(Node):
    """
    Day 5 最小任务编排器。

    流程：
    1. 确认 joint_states 正在持续发布；
    2. 调用 QueryObjectPose Service 获取物体位姿；
    3. 将位姿送入 ExecutePick Action；
    4. 打印阶段反馈和最终结果。
    """

    def __init__(self):
        super().__init__('pick_task_client')

        self.declare_parameter('object_id', 'demo_cube')
        self.declare_parameter('use_learned_local_skill', False)
        self.declare_parameter('wait_timeout_sec', 5.0)

        self.object_id = str(
            self.get_parameter('object_id').value
        )
        self.use_learned_local_skill = bool(
            self.get_parameter('use_learned_local_skill').value
        )
        self.wait_timeout_sec = float(
            self.get_parameter('wait_timeout_sec').value
        )

        self.latest_joint_state = None

        self.joint_state_subscription = self.create_subscription(
            JointState,
            'joint_states',
            self.on_joint_state,
            10,
        )

        self.pose_client = self.create_client(
            QueryObjectPose,
            'query_object_pose',
        )

        self.pick_client = ActionClient(
            self,
            ExecutePick,
            'execute_pick',
        )

        self.get_logger().info(
            'pick_task_client created with '
            f"object_id='{self.object_id}', "
            f'use_learned_local_skill='
            f'{self.use_learned_local_skill}.'
        )

    def on_joint_state(self, message):
        self.latest_joint_state = message

    def wait_for_joint_state(self):
        deadline = monotonic() + self.wait_timeout_sec

        while rclpy.ok() and monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)

            if self.latest_joint_state is not None:
                joint_count = len(self.latest_joint_state.name)

                self.get_logger().info(
                    'Received first joint state: '
                    f'joint_count={joint_count}.'
                )
                return True

        self.get_logger().error(
            'Task stopped: no /joint_states received before timeout.'
        )
        return False

    def run_task(self):
        if not self.wait_for_joint_state():
            return 1

        if not self.pose_client.wait_for_service(
            timeout_sec=self.wait_timeout_sec
        ):
            self.get_logger().error(
                'Task stopped: /query_object_pose service is unavailable.'
            )
            return 2

        pose_request = QueryObjectPose.Request()
        pose_request.object_id = self.object_id

        self.get_logger().info(
            f"Querying pose for object_id='{self.object_id}'."
        )

        pose_future = self.pose_client.call_async(pose_request)

        rclpy.spin_until_future_complete(
            self,
            pose_future,
            timeout_sec=self.wait_timeout_sec,
        )

        if not pose_future.done():
            self.get_logger().error(
                'Task stopped: pose query timed out.'
            )
            return 3

        pose_response = pose_future.result()

        if pose_response is None:
            self.get_logger().error(
                'Task stopped: pose query returned no response.'
            )
            return 4

        if not pose_response.success:
            self.get_logger().error(
                'Task stopped: pose query failed: '
                f'{pose_response.message}'
            )
            return 5

        position = pose_response.pose.pose.position

        self.get_logger().info(
            'Pose resolved: '
            f"frame_id='{pose_response.pose.header.frame_id}', "
            f'x={position.x:.3f}, '
            f'y={position.y:.3f}, '
            f'z={position.z:.3f}.'
        )

        if not self.pick_client.wait_for_server(
            timeout_sec=self.wait_timeout_sec
        ):
            self.get_logger().error(
                'Task stopped: /execute_pick action server is unavailable.'
            )
            return 6

        goal = ExecutePick.Goal()
        goal.object_pose = pose_response.pose

        # Day 5 的最小 Demo 中，对象 ID 与对象类别使用同一名称。
        # 后续接入真实感知时，会将 object_id 与 object_class 分开。
        goal.object_class = self.object_id
        goal.use_learned_local_skill = self.use_learned_local_skill

        self.get_logger().info(
            'Sending ExecutePick goal.'
        )

        goal_future = self.pick_client.send_goal_async(
            goal,
            feedback_callback=self.on_feedback,
        )

        rclpy.spin_until_future_complete(
            self,
            goal_future,
            timeout_sec=self.wait_timeout_sec,
        )

        if not goal_future.done():
            self.get_logger().error(
                'Task stopped: action goal request timed out.'
            )
            return 7

        goal_handle = goal_future.result()

        if goal_handle is None or not goal_handle.accepted:
            self.get_logger().error(
                'Task stopped: action goal was rejected.'
            )
            return 8

        result_future = goal_handle.get_result_async()

        rclpy.spin_until_future_complete(
            self,
            result_future,
            timeout_sec=self.wait_timeout_sec + 10.0,
        )

        if not result_future.done():
            self.get_logger().error(
                'Task stopped: action result timed out.'
            )
            return 9

        wrapped_result = result_future.result()

        if wrapped_result is None:
            self.get_logger().error(
                'Task stopped: action returned no result.'
            )
            return 10

        result = wrapped_result.result

        if result.success:
            self.get_logger().info(
                'Task succeeded: '
                f'candidate={result.selected_candidate_id}, '
                f'planning_time={result.planning_time:.3f}s.'
            )
            return 0

        self.get_logger().error(
            'Task failed: '
            f'failure_code={result.failure_code}, '
            f'planning_time={result.planning_time:.3f}s.'
        )
        return 11

    def on_feedback(self, feedback_message):
        feedback = feedback_message.feedback

        self.get_logger().info(
            f'Action feedback: phase={feedback.phase}, '
            f'progress={feedback.progress:.2f}.'
        )


def main(args=None):
    rclpy.init(args=args)

    node = PickTaskClient()
    exit_code = 1

    try:
        exit_code = node.run_task()
    except KeyboardInterrupt:
        node.get_logger().warning('Task interrupted by user.')
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

    return exit_code


if __name__ == '__main__':
    main()