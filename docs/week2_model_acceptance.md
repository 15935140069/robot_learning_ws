
Week 2 机器人模型验收记录
1. 验收范围

本周完成 UR5e 机械臂、教学用平行夹爪、TCP、固定外置相机、
URDF/Xacro、RViz 显示、TF 坐标树与相机点坐标变换验证。

本周不包含真实相机标定、视觉识别、MoveIt、ros2_control、碰撞规划、
动力学仿真和强化学习。

2. 静态模型验收

已使用以下命令验证完整 URDF：

python3 scripts/verify_week2_model.py /tmp/week2_full.urdf

检查结果全部通过：

UR5e 自维护 mesh 引用数量为 14。
未残留 ur_description 旧包路径。
UR5e 本体、夹爪和相机均包含 visual、collision、inertial。
6 个 UR5e 转动关节均包含 axis 与 limit。
两个夹爪直线关节行程均为 0~0.03 m。
tool0 -> gripper_base_link -> tcp 父子关系正确。
base_link -> camera_link -> camera_optical_frame 父子关系正确。
3. 动态与 TF 验收

RViz 中已验证：

RobotModel 与 TF 状态均为 OK。
关节滑块可以驱动 6 个机械臂关节和 2 个夹爪关节。
机械臂运动时，夹爪与 TCP 随末端连续运动。
固定外置相机保持在 base_link 下，不随机械臂运动。
已生成 TF 树文件：artifacts/week2_tf/week2_tf_tree.pdf。

已验证的关键坐标链：

world -> base_link -> ... -> tool0 -> gripper_base_link -> tcp
world -> base_link -> camera_link -> camera_optical_frame
4. Day 4 坐标变换验证

输入点：

camera_optical_frame 中 [0.0, 0.0, 1.0] m

TF 程序输出：

base_link 中 [0.163907, -0.071523, 0.227313] m

最大绝对误差：

0.000477 m，约 0.477 mm

小于 2 mm 容许误差，因此相机坐标点到机械臂基座坐标的变换验证通过。

5. 固定验收姿态
artifacts/week2_tf/week2_zero_pose.yaml：全关节零位基准姿态。
artifacts/week2_tf/week2_inspection_pose.yaml：非零验收姿态。

验收姿态中左右夹爪关节约为 0.015 m，二者相差约 0.162 mm，
属于 GUI 滑块精度造成的微小差异，可视为对称开合。

6. 当前限制
夹爪左右手指仍为两个独立的直线关节，尚未加入 mimic 联动。
相机位姿为学习用临时安装位姿，不是实际标定结果。
尚未接入 ros2_control、MoveIt、碰撞规划、真实视觉或物理仿真。
7. 结论

Week 2 的机器人描述、夹爪、TCP、相机、RViz 与 TF 基础链路验收通过。
在进入 MoveIt 或控制相关工作前，应保持本周建立的坐标系语义和 TF 链不变。
