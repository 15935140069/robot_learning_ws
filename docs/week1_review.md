# Week 1：ROS2 基础与可观察系统复盘

## 1. 本周完成内容

本周完成了一个最小 ROS2 抓取任务系统，包含：

- `joint_state_mock_publisher`：持续发布 6 轴模拟关节状态；
- `pose_query_service`：根据对象 ID 返回 `PoseStamped`；
- `execute_pick_action_server`：执行最小抓取任务并发布阶段反馈；
- `pick_task_client`：串联关节状态检查、位姿查询和抓取 Action；
- `bringup.launch.py`：一键启动整套系统；
- normal/debug 两份 YAML 参数配置；
- `rqt_graph` 节点关系图；
- rosbag2 录制、检查与回放；
- Action 结构化失败码和 JSON 事件日志。

## 2. Topic、Service、Action 的使用边界

### Topic

Topic 用于持续变化的数据流。

本项目中 `/joint_states` 持续发布关节位置和速度，因此使用 Topic。订阅方不需要请求，发布方也不需要等待响应。

### Service

Service 用于一次请求、一次响应的短操作。

本项目中 `/query_object_pose` 根据对象 ID 查询对象位姿，调用后立即得到成功状态、位姿或失败信息，因此使用 Service。

### Action

Action 用于耗时任务，需要过程反馈、最终结果和取消能力。

本项目中 `/execute_pick` 需要经历 RESET、SELECT_CANDIDATE、PLAN_PREGRASP、APPROACH、CLOSE_GRIPPER、LIFT 等阶段，因此使用 Action。

## 3. 本周任务链路

```text
/joint_states 在线
        ↓
QueryObjectPose 查询 demo_cube 位姿
        ↓
ExecutePick 接收 PoseStamped 与 object_class
        ↓
持续返回 Feedback phase
        ↓
返回 success、failure_code、candidate_id、planning_time