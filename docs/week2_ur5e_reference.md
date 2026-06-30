# Week 2 / Day 1：UR5e 参考模型阅读笔记

## 参考来源

参考仓库仅用于阅读：

```text
third_party_reference/ur_description_reference

第三方仓库不放入 src/，不参与本项目构建，也不直接修改。

官方模型结构
ur.urdf.xacro
  └─ ur_macro.xacro
      └─ ur_robot 宏
          └─ 读取 config/ur5e 下的参数文件
UR5e 六轴运动链
base_link
→ shoulder_pan_joint
→ shoulder_link
→ shoulder_lift_joint
→ upper_arm_link
→ elbow_joint
→ forearm_link
→ wrist_1_joint
→ wrist_1_link
→ wrist_2_joint
→ wrist_2_link
→ wrist_3_joint
→ wrist_3_link
→ flange
→ tool0
标签职责
标签	作用
link	机械臂的刚体零件或坐标参考体
joint	父 link 与子 link 的连接关系
origin	子关节相对父 link 的位置和姿态
axis	关节在局部坐标系中的旋转轴
limit	关节角度、速度、力矩等边界
visual	RViz 显示模型
collision	后续碰撞检测使用的几何体
inertial	后续物理仿真使用的质量与惯量