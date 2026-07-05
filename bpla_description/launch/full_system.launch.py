import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command
from launch.actions import TimerAction

def generate_launch_description():
    pkg_dir = get_package_share_directory('bpla_description')
    urdf_path = os.path.join(pkg_dir, 'urdf', 'quadcopter.urdf')

    propeller_bridge = Node(
        package='bpla_propeller',
        executable='propeller_joint_bridge.py',
        name='propeller_joint_bridge',
        output='screen'
    )

    robot_state_pub = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': ParameterValue(
                Command(['cat ', urdf_path]),
                value_type=str
            )
        }]
    )

    # Запускаем robot_state_publisher с задержкой 2 секунды
    delayed_rsp = TimerAction(
        period=2.0,
        actions=[robot_state_pub]
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        propeller_bridge,
        delayed_rsp,
        rviz,
    ])
