# SPDX-License-Identifier: Apache-2.0
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    share = get_package_share_directory('autopartol_robot')
    clock = LaunchConfiguration('use_sim_time')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('config_file', default_value=os.path.join(share, 'config', 'patrol_config.yaml')),
        DeclareLaunchArgument('speech_backend', default_value='log', choices=['log', 'espeak', 'edge']),
        Node(package='autopartol_robot', executable='patrol_node', output='screen',
             parameters=[LaunchConfiguration('config_file'), {'use_sim_time': clock}]),
        Node(package='autopartol_robot', executable='speaker', output='screen',
             parameters=[{'use_sim_time': clock, 'backend': LaunchConfiguration('speech_backend')}]),
    ])
