import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

def generate_launch_description():
    
    package_name = 'real_test_robot'

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value='line_follow.sdf',
        description='SDF world file'
    )

    # Gazebo
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'),'launch', 'gz_sim.launch.py')]),
            launch_arguments={'gz_args': ['-r -v4', world], 'on_exit_shutdown': 'true'}.items(),
    )

    # Spawn robot into Gazebo
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'real_test_robot',
            '-topic', '/robot_description',
            '-x', '0', '-y', '0', '-z', '0.1'
        ],
        output='screen'
    )

    # RViz
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        additional_env={'DISPLAY': ':1', 'LIBGL_ALWAYS_SOFTWARE': '1'}
    )

    # Bridge
    bridge_params = os.path.join(get_package_share_directory(package_name),'config','gz_bridge.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ]
    )



    return LaunchDescription([
        rsp,
        world_arg,
        gazebo,
        spawn_robot,
        rviz,
        ros_gz_bridge
    ])