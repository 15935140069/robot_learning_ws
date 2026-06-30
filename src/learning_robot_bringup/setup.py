import os
from glob import glob

from setuptools import find_packages, setup


package_name = 'learning_robot_bringup'


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            os.path.join('share', package_name),
            ['package.xml'],
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py'),
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='renyinjie',
    maintainer_email='15935140069@163.com',
    description=(
        'ROS2 bringup, launch files, parameters, '
        'and Week 1 communication demos.'
    ),
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'health_check = learning_robot_bringup.health_check:main',
            'joint_state_mock_publisher = '
            'learning_robot_bringup.joint_state_mock_publisher:main',
            'pose_query_service = '
            'learning_robot_bringup.pose_query_service:main',
            'execute_pick_action_server = '
            'learning_robot_bringup.execute_pick_action_server:main',
            'pick_task_client = learning_robot_bringup.pick_task_client:main',
        ],
    },
)