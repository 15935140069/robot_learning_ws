# 使用 source 加载本文件，不要直接执行。
# 目的：统一 ROS2 Jazzy + Cyclone DDS 开发环境。

if [ -n "${CONDA_PREFIX:-}" ] && command -v conda >/dev/null 2>&1; then
    conda deactivate
fi

source /opt/ros/jazzy/setup.bash
source ~/robot_learning_ws/install/setup.bash

unset ROS_LOCALHOST_ONLY
unset ROS_DISCOVERY_SERVER
unset ROS_STATIC_PEERS
unset FASTRTPS_DEFAULT_PROFILES_FILE
unset CYCLONEDDS_URI

export ROS_DOMAIN_ID=42
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo "ROS environment ready:"
echo "  ROS_DISTRO=$ROS_DISTRO"
echo "  ROS_DOMAIN_ID=$ROS_DOMAIN_ID"
echo "  ROS_AUTOMATIC_DISCOVERY_RANGE=$ROS_AUTOMATIC_DISCOVERY_RANGE"
echo "  RMW_IMPLEMENTATION=$RMW_IMPLEMENTATION"
