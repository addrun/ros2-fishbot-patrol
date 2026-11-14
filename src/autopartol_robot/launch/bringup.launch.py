# SPDX-License-Identifier: Apache-2.0
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    def include(package, file, arguments, **kwargs):
        path = os.path.join(get_package_share_directory(package), 'launch', file)
        return IncludeLaunchDescription(PythonLaunchDescriptionSource(path),
                                        launch_arguments=arguments.items(), **kwargs)
    options = [DeclareLaunchArgument(name, default_value=value) for name, value in [
        ('gui', 'true'), ('rviz', 'true'), ('headless', 'false'),
        ('use_sim_time', 'true'), ('patrol', 'true'), ('speech_backend', 'log')]]
    options.append(DeclareLaunchArgument('config_file', default_value=os.path.join(
        get_package_share_directory('autopartol_robot'), 'config', 'patrol_config.yaml')))
    options += [
        include('fishbot_description', 'gazebo_sim.launch.py',
                {name: LaunchConfiguration(name) for name in ['gui', 'headless', 'use_sim_time']}),
        include('fishbot_navigation2', 'navigation2.launch.py',
                {name: LaunchConfiguration(name) for name in ['rviz', 'use_sim_time']}),
        include('autopartol_robot', 'autopatrol.launch.py',
                {name: LaunchConfiguration(name) for name in ['use_sim_time', 'speech_backend', 'config_file']},
                condition=IfCondition(LaunchConfiguration('patrol'))),
    ]
    return LaunchDescription(options)
