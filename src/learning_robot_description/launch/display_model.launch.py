from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_name = LaunchConfiguration("robot_name")
    ur_type = LaunchConfiguration("ur_type")
    tf_prefix = LaunchConfiguration("tf_prefix")
    use_gripper = LaunchConfiguration("use_gripper")
    use_camera = LaunchConfiguration("use_camera")
    rviz_config = LaunchConfiguration("rviz_config")

    package_share = FindPackageShare("learning_robot_description")

    model_xacro = PathJoinSubstitution(
        [
            package_share,
            "urdf",
            "robot_with_gripper_camera.urdf.xacro",
        ]
    )

    default_rviz_config = PathJoinSubstitution(
        [
            package_share,
            "rviz",
            "learning_ur5e.rviz",
        ]
    )

    robot_description = ParameterValue(
        Command(
            [
                FindExecutable(name="xacro"),
                " ",
                model_xacro,
                " ",
                "name:=",
                robot_name,
                " ",
                "ur_type:=",
                ur_type,
                " ",
                "tf_prefix:=",
                tf_prefix,
                " ",
                "use_gripper:=",
                use_gripper,
                " ",
                "use_camera:=",
                use_camera,
            ]
        ),
        value_type=str,
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_name",
                default_value="learning_ur5e",
                description="Robot name used in the URDF.",
            ),
            DeclareLaunchArgument(
                "ur_type",
                default_value="ur5e",
                description="Universal Robots model type.",
            ),
            DeclareLaunchArgument(
                "tf_prefix",
                default_value="",
                description="Optional TF frame prefix.",
            ),
            DeclareLaunchArgument(
                "use_gripper",
                default_value="true",
                description="Load the teaching parallel gripper.",
            ),
            DeclareLaunchArgument(
                "use_camera",
                default_value="true",
                description="Load the fixed external camera.",
            ),
            DeclareLaunchArgument(
                "rviz_config",
                default_value=default_rviz_config,
                description="Path to the RViz configuration file.",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                output="screen",
                parameters=[
                    {
                        "robot_description": robot_description,
                        "publish_frequency": 30.0,
                    }
                ],
            ),
            Node(
                package="joint_state_publisher_gui",
                executable="joint_state_publisher_gui",
                name="joint_state_publisher_gui",
                output="screen",
                parameters=[{"robot_description": robot_description}],
            ),
            Node(
                package="rviz2",
                executable="rviz2",
                name="rviz2",
                output="screen",
                arguments=["-d", rviz_config],
            ),
        ]
    )
