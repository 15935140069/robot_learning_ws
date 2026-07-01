# 坐标系约定说明

## Week 2 坐标树

```text
world
└── base_link
    ├── UR5e 机械臂关节链
    │   └── tool0
    │       └── gripper_base_link
    │           └── tcp
    └── camera_link
        └── camera_optical_frame
各坐标系含义
world：仿真场景根坐标系。
base_link：UR5e 机械臂基座坐标系，X 轴向前、Y 轴向左、Z 轴向上。
tool0：UR5e 自带的末端工具安装参考坐标系。
gripper_base_link：教学用平行夹爪的基座坐标系。
tcp：夹爪任务中心点，位于两指之间、靠近夹爪前端。
camera_link：固定外置相机的机械安装坐标系。
camera_optical_frame：相机光学坐标系，X 轴向右、Y 轴向下、Z 轴沿拍摄方向向前。
变换写法

T_A_B 表示“将 B 坐标系中的坐标转换到 A 坐标系”。

p_A = T_A_B @ p_B

Day 4 验证采用：

p_base_link =
T_base_link_camera_optical_frame @
p_camera_optical_frame

输入点为相机正前方 1 m：

p_camera_optical_frame = [0.0, 0.0, 1.0] m

程序输出：

p_base_link = [0.163907, -0.071523, 0.227313] m

与手算参考值 [0.164000, -0.072000, 0.227000] m 的最大误差为
0.000477 m，即约 0.477 mm，小于设定的 2 mm 容许误差。

注意：以上数值只适用于当前学习项目中的临时相机安装位姿。后续修改相机位置、姿态或标定参数后，必须重新执行 TF 验证。
