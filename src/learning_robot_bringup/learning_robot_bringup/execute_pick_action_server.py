import json
import logging
from pathlib import Path
from time import perf_counter, sleep

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from learning_robot_bringup.pick_failure_codes import PickFailureCode
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
        self.declare_parameter(
            'event_log_path',
            '~/.ros/robot_learning_logs/execute_pick.log',
        )

        self.stage_delay_sec = float(
            self.get_parameter('stage_delay_sec').value
        )
        self.debug = bool(
            self.get_parameter('debug').value
        )
        self.event_log_path = Path(
            str(self.get_parameter('event_log_path').value)
        ).expanduser()

        self.event_logger = self.create_event_logger(
            self.event_log_path
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
        self.write_event(
            'server_started',
            stage_delay_sec=self.stage_delay_sec,
            debug=self.debug,
            event_log_path=str(self.event_log_path),
        )
    def create_event_logger(self, event_log_path):
        event_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(
            'learning_robot_bringup.execute_pick_action_server'
        )
        logger.setLevel(logging.INFO)
        logger.propagate = False

        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            handler.close()

        file_handler = logging.FileHandler(
            event_log_path,
            encoding='utf-8',
        )
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s %(message)s'
            )
        )
        logger.addHandler(file_handler)

        return logger


    def write_event(self, event_name, **fields):
        record = {
            'event': event_name,
            'node': self.get_name(),
            **fields,
        }

        self.event_logger.info(
            json.dumps(
                record,
                ensure_ascii=False,
                sort_keys=True,
            )
        )



    def goal_callback(self, goal_request):
        object_class = goal_request.object_class.strip()
        frame_id = goal_request.object_pose.header.frame_id.strip()

        if not object_class:
            self.get_logger().warning(
                'Rejected goal: object_class is empty.'
            )
            self.write_event(
                'goal_rejected',
                reason='object_class is empty',
            )
            return GoalResponse.REJECT

        if not frame_id:
            self.get_logger().warning(
                'Rejected goal: object_pose.header.frame_id is empty.'
            )
            self.write_event(
                'goal_rejected',
                reason='object_pose.header.frame_id is empty',
                object_class=object_class,
            )
            return GoalResponse.REJECT

        self.get_logger().info(
            f"Accepted goal: object_class='{object_class}', "
            f"frame_id='{frame_id}', "
            f"use_learned_local_skill="
            f'{goal_request.use_learned_local_skill}'
        )

        self.write_event(
            'goal_accepted',
            object_class=object_class,
            frame_id=frame_id,
            use_learned_local_skill=bool(
                goal_request.use_learned_local_skill
            ),
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

        self.write_event(
            'feedback_published',
            phase=phase,
            progress=round(float(progress), 2),
        )

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
                'The Day 4 mock server does not run a learned policy.'
            )
            self.write_event(
                'learned_skill_requested',
                object_class=object_class,
                mode='mock_fallback',
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
                failure_code = PickFailureCode.CANCELED.value

                self.get_logger().warning(
                    f'Goal canceled during phase={phase}.'
                )
                self.write_event(
                    'goal_canceled',
                    object_class=object_class,
                    phase=phase,
                    failure_code=failure_code,
                    planning_time=round(elapsed, 3),
                )

                return self.make_result(
                    success=False,
                    failure_code=failure_code,
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
                failure_code = PickFailureCode.NO_CANDIDATE.value

                self.get_logger().warning(
                    f"Goal aborted: {failure_code} "
                    f"for '{object_class}'."
                )
                self.write_event(
                    'goal_aborted',
                    object_class=object_class,
                    phase=phase,
                    failure_code=failure_code,
                    planning_time=round(elapsed, 3),
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
        failure_code = PickFailureCode.NONE.value

        self.get_logger().info(
            f"Goal succeeded for '{object_class}', "
            f'candidate={candidate_id}.'
        )
        self.write_event(
            'goal_succeeded',
            object_class=object_class,
            selected_candidate_id=candidate_id,
            failure_code=failure_code,
            planning_time=round(elapsed, 3),
        )

        return self.make_result(
            success=True,
            failure_code=failure_code,
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