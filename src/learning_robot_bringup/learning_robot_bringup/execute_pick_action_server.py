from time import perf_counter, sleep

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from learning_robot_interfaces.action import ExecutePick


class ExecutePickActionServer(Node):
    """
    Day 2：最小抓取任务 Action Server。

    当前不连接真实机械臂、MoveIt 或夹爪。
    仅模拟一个可观察的抓取任务流程：
    接收 Goal -> 连续发布 Feedback -> 返回 Result。
    """

    def __init__(self):
        super().__init__('execute_pick_action_server')

        self.callback_group = ReentrantCallbackGroup()

        self.action_server = ActionServer(
            self,
            ExecutePick,
            '/execute_pick',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )

        self.get_logger().info(
            'execute_pick_action_server started: waiting for /execute_pick goals.'
        )

    def goal_callback(self, goal_request):
        # object_class：物体类别，例如 demo_cube
        object_class = goal_request.object_class.strip()
        # frame_id：物体位姿属于哪个坐标系，例如 base_link
        frame_id = goal_request.object_pose.header.frame_id.strip()

        if not object_class:
            self.get_logger().warning('Rejected goal: object_class is empty.')
            return GoalResponse.REJECT

        if not frame_id:
            self.get_logger().warning(
                'Rejected goal: object_pose.header.frame_id is empty.'
            )
            return GoalResponse.REJECT

        self.get_logger().info(
            f"Accepted goal: object_class='{object_class}', "
            f"frame_id='{frame_id}', "
            f"use_learned_local_skill={goal_request.use_learned_local_skill}"
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
                'Day 2 mock server does not execute a learned policy yet.'
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
            sleep(0.8)

            # Day 2 的可控失败分支：
            # 只有 demo_cube 有预设抓取候选。
            if phase == 'SELECT_CANDIDATE' and object_class != 'demo_cube':
                goal_handle.abort()

                elapsed = perf_counter() - start_time
                failure_code = 'NO_CANDIDATE'

                self.get_logger().warning(
                    f"Goal aborted: {failure_code} for '{object_class}'."
                )

                return self.make_result(
                    success=False,
                    failure_code=failure_code,
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