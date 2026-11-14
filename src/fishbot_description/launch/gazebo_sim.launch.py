# SPDX-License-Identifier: Apache-2.0
import os
import shlex
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def start_gazebo(context):
    arguments = ['-r', '-v', '2']
    if LaunchConfiguration('gui').perform(context).lower() == 'false':
        arguments.append('-s')
    if LaunchConfiguration('headless').perform(context).lower() == 'true':
        arguments.append('--headless-rendering')
    arguments.append(LaunchConfiguration('world').perform(context))
    launch = os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    return [IncludeLaunchDescription(PythonLaunchDescriptionSource(launch),
            launch_arguments={'gz_args': shlex.join(arguments)}.items())]

def generate_launch_description():
    share = get_package_share_directory('fishbot_description')
    clock = LaunchConfiguration('use_sim_time')
    return LaunchDescription([
        DeclareLaunchArgument('gui', default_value='true', choices=['true', 'false']),
        DeclareLaunchArgument('headless', default_value='false', choices=['true', 'false']),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('world', default_value=os.path.join(share, 'world', 'room', 'custom_room.sdf')),
        DeclareLaunchArgument('model', default_value=os.path.join(share, 'urdf', 'fishbot', 'fishbot.urdf.xacro')),
        OpaqueFunction(function=start_gazebo),
        Node(package='robot_state_publisher', executable='robot_state_publisher', output='screen',
             parameters=[{'use_sim_time': clock, 'robot_description': ParameterValue(
                 Command(['xacro ', LaunchConfiguration('model')]), value_type=str)}]),
        Node(package='ros_gz_sim', executable='create', output='screen',
             arguments=['-topic', 'robot_description', '-name', 'fishbot', '-z', '0.2']),
        Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
             parameters=[{'use_sim_time': clock, 'config_file': os.path.join(share, 'config', 'ros_gz_bridge.yaml')}]),
        Node(package='controller_manager', executable='spawner', output='screen',
             arguments=['fishbot_joint_state_broadcaster', '--controller-manager-timeout', '60']),
        Node(package='controller_manager', executable='spawner', output='screen',
             arguments=['fishbot_diff_drive_controller', '--controller-manager-timeout', '60',
                            '--controller-ros-args', '-r ~/odom:=/odom']),
        Node(package='fishbot_description', executable='vel_helper.py', output='screen',
             parameters=[{'use_sim_time': clock}]),
    ])
