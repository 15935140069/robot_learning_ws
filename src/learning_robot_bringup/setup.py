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
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='renyinjie',
    maintainer_email='renyinjie@example.com',
    description='ROS2 bringup, launch files, parameters, and Week 1 communication demos.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'health_check = learning_robot_bringup.health_check:main',
        ],
    },
)
