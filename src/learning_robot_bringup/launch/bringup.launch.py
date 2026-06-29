import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    package_share_directory = get_package_share_directory(
        'learning_robot_bringup'
    )

    default_config_file = os.path.join(
        package_share_directory,
        'config',
        'normal.yaml',
    )

    config_file = LaunchConfiguration('config_file')
    namespace = LaunchConfiguration('namespace')
    joint_states_topic = LaunchConfiguration('joint_states_topic')

    return LaunchDescription([
        DeclareLaunchArgument(
            'config_file',
            default_value=default_config_file,
            description='YAML parameter file for all nodes.',
        ),
        DeclareLaunchArgument(
            'namespace',
            default_value='',
            description='ROS namespace for the Day 3 demo nodes.',
        ),
        DeclareLaunchArgument(
            'joint_states_topic',
            default_value='joint_states',
            description='Remapped output topic of joint_state_mock_publisher.',
        ),

        Node(
            package='learning_robot_bringup',
            executable='joint_state_mock_publisher',
            name='joint_state_mock_publisher',
            namespace=namespace,
            output='screen',
            parameters=[config_file],
            remappings=[
                ('joint_states', joint_states_topic),
            ],
        ),

        Node(
            package='learning_robot_bringup',
            executable='pose_query_service',
            name='pose_query_service',
            namespace=namespace,
            output='screen',
            parameters=[config_file],
        ),

        Node(
            package='learning_robot_bringup',
            executable='execute_pick_action_server',
            name='execute_pick_action_server',
            namespace=namespace,
            output='screen',
            parameters=[config_file],
        ),

        Node(
            package='learning_robot_bringup',
            executable='health_check',
            name='rviz_placeholder',
            namespace=namespace,
            output='screen',
        ),
    ])