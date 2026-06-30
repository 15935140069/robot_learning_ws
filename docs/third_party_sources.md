# Third-party model resources

## Universal Robots ROS2 Description

Source repository:
https://github.com/UniversalRobots/Universal_Robots_ROS2_Description.git

Copied into this project for learning use:
- src/learning_robot_description/urdf/ur_macro.xacro
- src/learning_robot_description/urdf/inc/ur_common.xacro
- src/learning_robot_description/config/ur5e/
- src/learning_robot_description/meshes/ur5e/

Local modifications:
- Replaced package references from `ur_description` to `learning_robot_description`.
- Kept UR5e link, joint, origin, axis, limit, inertial, visual, and collision structure unchanged as much as possible.

Note:
`flange` in the URDF is the robot wrist mounting flange frame, not a grasp target object.
