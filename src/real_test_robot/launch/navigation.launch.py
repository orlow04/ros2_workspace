import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'real_test_robot'

    map_file = LaunchConfiguration('map')
    world = LaunchConfiguration('world')

    map_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(
            get_package_share_directory(package_name), 'maps', 'arena_map.yaml'
        ),
        description='Full path to map yaml file'
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='arena.sdf',
        description='SDF world file'
    )

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]),
        launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'false'}.items()
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'
        )]),
        launch_arguments={'gz_args': ['-r -v4 ', world], 'on_exit_shutdown': 'true'}.items(),
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-name', 'real_test_robot', '-topic', '/robot_description',
                   '-x', '0', '-y', '0', '-z', '0.1'],
        output='screen'
    )

    bridge_params = os.path.join(get_package_share_directory(package_name), 'config', 'gz_bridge.yaml')
    ros_gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=['--ros-args', '-p', f'config_file:={bridge_params}']
    )

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py'
        )]),
        launch_arguments={
            'map': map_file,
            'use_sim_time': 'true',
            'params_file': os.path.join(
                get_package_share_directory(package_name), 'config', 'nav2_params.yaml'
            ),
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        additional_env={'DISPLAY': ':1', 'LIBGL_ALWAYS_SOFTWARE': '1'}
    )

    return LaunchDescription([
        map_arg,
        world_arg,
        rsp,
        gazebo,
        spawn_robot,
        ros_gz_bridge,
        nav2,
        rviz,
    ])