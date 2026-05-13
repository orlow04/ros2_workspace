import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'real_test_robot'

    use_sim_time = LaunchConfiguration('use_sim_time')
    world = LaunchConfiguration('world')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name), 'launch', 'rsp.launch.py'
        )]),
        launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'false'}.items()
    )

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='arena.sdf',
        description='SDF world file'
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

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py'
        )]),
        launch_arguments={
            'slam_params_file': os.path.join(
                get_package_share_directory(package_name),
                'config', 'mapper_params_online_async.yaml'
            ),
            'use_sim_time': 'true'
        }.items()
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        additional_env={'DISPLAY': ':1', 'LIBGL_ALWAYS_SOFTWARE': '1'}
    )

    return LaunchDescription([
        world_arg,
        rsp,
        gazebo,
        spawn_robot,
        ros_gz_bridge,
        slam,
        rviz,
    ])