# robot_learning_ws

ROS2 + MoveIt2 + 仿真抓取与局部强化学习项目工作空间。

## 当前阶段

当前完成：第 1 周 Day 1  
目标：建立 ROS2 Jazzy 工作空间、基础包、构建纪律和可观察通信环境。

本周暂不引入：

- URDF / Xacro
- MoveIt2
- Gazebo Sim
- MuJoCo
- PPO
- GraspNet

## 目录说明

```text
robot_learning_ws/
├── src/
│   ├── learning_robot_interfaces/   # 后续 msg / srv / action 接口
│   └── learning_robot_bringup/      # Python 节点、launch、参数与启动入口
├── docs/                            # 学习笔记、节点图、复盘
├── scripts/
│   └── ros_jazzy_env.sh             # ROS2 Jazzy 开发环境加载脚本
├── build/                           # colcon 构建产物，不提交 Git
├── install/                         # 安装覆盖层，不提交 Git
└── log/                             # 构建日志，不提交 Git

