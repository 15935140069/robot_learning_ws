from time import perf_counter, sleep

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from learning_robot_interfaces.action import ExecutePick


class ExecutePickActionServer(Node):
    """
    Day 3：由 YAML 参数配置的最小抓取任务 Action Server。

    当前只模拟任务编排：
    接收 Goal -> 发布 Feedback -> 返回成功或结构化失败结果。
    """

    def __init__(self):
        super().__init__('execute_pick_action_server')

        self.declare_parameter('stage_delay_sec', 0.8)
        self.declare_parameter('debug', False)

        self.stage_delay_sec = float(
            self.get_parameter('stage_delay_sec').value
        )
        self.debug = bool(
            self.get_parameter('debug').value
        )

        if self.stage_delay_sec <= 0.0:
            raise ValueError(
                'stage_delay_sec must be greater than 0.'
            )

        self.callback_group = ReentrantCallbackGroup()

        self.action_server = ActionServer(
            self,
            ExecutePick,
            'execute_pick',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )

        self.get_logger().info(
            'execute_pick_action_server started with '
            f'stage_delay_sec={self.stage_delay_sec}, '
            f'debug={self.debug}.'
        )

    def goal_callback(self, goal_request):
        object_class = goal_request.object_class.strip()
        frame_id = goal_request.object_pose.header.frame_id.strip()

        if not object_class:
            self.get_logger().warning(
                'Rejected goal: object_class is empty.'
            )
            return GoalResponse.REJECT

        if not frame_id:
            self.get_logger().warning(
                'Rejected goal: object_pose.header.frame_id is empty.'
            )
            return GoalResponse.REJECT

        self.get_logger().info(
            f"Accepted goal: object_class='{object_class}', "
            f"frame_id='{frame_id}', "
            f"use_learned_local_skill="
            f'{goal_request.use_learned_local_skill}'
        )

        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().warning('Cancel request accepted.')
        return CancelResponse.ACCEPT

    def publish_feedback(self, goal_handle, phase, progress):
        feedback = ExecutePick.Feedback()
        feedback.phase = phase
        feedback.progress = float(progress)

        goal_handle.publish_feedback(feedback)

        if self.debug:
            self.get_logger().info(
                f'Feedback: phase={phase}, progress={progress:.2f}'
            )

    def make_result(
        self,
        success,
        failure_code,
        selected_candidate_id,
        planning_time,
    ):
        result = ExecutePick.Result()
        result.success = success
        result.failure_code = failure_code
        result.selected_candidate_id = selected_candidate_id
        result.planning_time = float(planning_time)
        return result

    def execute_callback(self, goal_handle):
        start_time = perf_counter()
        goal = goal_handle.request
        object_class = goal.object_class.strip()

        if goal.use_learned_local_skill:
            self.get_logger().info(
                'use_learned_local_skill=True received. '
                'The Day 3 mock server does not run a learned policy.'
            )

        stages = [
            ('RESET', 0.00),
            ('SELECT_CANDIDATE', 0.20),
            ('PLAN_PREGRASP', 0.45),
            ('APPROACH', 0.70),
            ('CLOSE_GRIPPER', 0.85),
            ('LIFT', 1.00),
        ]

        for phase, progress in stages:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()

                elapsed = perf_counter() - start_time
                self.get_logger().warning(
                    f'Goal canceled during phase={phase}.'
                )

                return self.make_result(
                    success=False,
                    failure_code='CANCELED',
                    selected_candidate_id='',
                    planning_time=elapsed,
                )

            self.publish_feedback(goal_handle, phase, progress)
            sleep(self.stage_delay_sec)

            if (
                phase == 'SELECT_CANDIDATE'
                and object_class != 'demo_cube'
            ):
                goal_handle.abort()

                elapsed = perf_counter() - start_time

                self.get_logger().warning(
                    f"Goal aborted: NO_CANDIDATE "
                    f"for '{object_class}'."
                )

                return self.make_result(
                    success=False,
                    failure_code='NO_CANDIDATE',
                    selected_candidate_id='',
                    planning_time=elapsed,
                )

        goal_handle.succeed()

        elapsed = perf_counter() - start_time
        candidate_id = 'rule_demo_cube_top_grasp_01'

        self.get_logger().info(
            f"Goal succeeded for '{object_class}', "
            f'candidate={candidate_id}.'
        )

        return self.make_result(
            success=True,
            failure_code='NONE',
            selected_candidate_id=candidate_id,
            planning_time=elapsed,
        )


def main(args=None):
    rclpy.init(args=args)

    node = ExecutePickActionServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()