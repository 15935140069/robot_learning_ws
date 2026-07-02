from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
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
    start_rviz = LaunchConfiguration("start_rviz")

    description_share = FindPackageShare("learning_robot_description")
    control_share = FindPackageShare("learning_robot_control")

    model_xacro = PathJoinSubstitution(
        [
            description_share,
            "urdf",
            "robot_with_gripper_camera.urdf.xacro",
        ]
    )

    controllers_file = PathJoinSubstitution(
        [
            control_share,
            "config",
            "controllers.yaml",
        ]
    )

    rviz_config = PathJoinSubstitution(
        [
            description_share,
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
                " ",
                "use_gripper:=true",
                " ",
                "use_camera:=true",
                " ",
                "use_ros2_control:=true",
            ]
        ),
        value_type=str,
    )

    robot_state_publisher = Node(
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
    )

    controller_manager = Node(
        package="controller_manager",
        executable="ros2_control_node",
        name="controller_manager",
        output="screen",
        parameters=[
            {"robot_description": robot_description},
            controllers_file,
        ],
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config],
        condition=IfCondition(start_rviz),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "robot_name",
                default_value="learning_ur5e",
            ),
            DeclareLaunchArgument(
                "ur_type",
                default_value="ur5e",
            ),
            DeclareLaunchArgument(
                "start_rviz",
                default_value="false",
                description="Launch RViz without joint_state_publisher_gui.",
            ),
            robot_state_publisher,
            controller_manager,
            rviz,
        ]
    )
