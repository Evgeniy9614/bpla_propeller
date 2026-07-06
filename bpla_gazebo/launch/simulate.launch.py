import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess, TimerAction
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command

def generate_launch_description():
    pkg_desc = get_package_share_directory('bpla_description')
    pkg_gazebo = get_package_share_directory('bpla_gazebo')
    urdf_path = os.path.join(pkg_desc, 'urdf', 'quadcopter.urdf')
    world_path = os.path.join(pkg_gazebo, 'worlds', 'empty_with_plugins.world')

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': ParameterValue(
            Command(['cat ', urdf_path]), value_type=str
        )}]
    )

    propeller_bridge = Node(
        package='bpla_propeller',
        executable='propeller_joint_bridge.py',
        name='propeller_joint_bridge',
        output='screen'
    )

    thrust_ctrl = Node(
        package='bpla_gazebo',
        executable='thrust_controller.py',
        name='thrust_controller',
        output='screen'
    )

    # Gazebo с ROS-плагинами (через -s)
    gazebo = ExecuteProcess(
        cmd=['gazebo', '--verbose', world_path,
             '-s', 'libgazebo_ros_init.so',
             '-s', 'libgazebo_ros_factory.so',
             '-s', 'libgazebo_ros_force_system.so'],
        output='screen'
    )

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'quadcopter', '-topic', 'robot_description'],
        output='screen'
    )

    return LaunchDescription([
        robot_state_pub,
        propeller_bridge,
        gazebo,
        TimerAction(period=5.0, actions=[spawn_entity]),
        TimerAction(period=8.0, actions=[thrust_ctrl]),
    ])
