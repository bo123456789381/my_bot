import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription,DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
def generate_launch_description():
    #create cli world:=...
    package_name = "my_bot"
    pkg_share = get_package_share_directory(package_name)
    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        "world",
        default_value='empty.sdf',
        description="World to load"
        )

    #include the robot_state_publisher launch file, provided by our own pkg. Force sim time to be enable

    rsp = IncludeLaunchDescription(
                PythonLaunchDescriptionSource([os.path.join(
                    get_package_share_directory(package_name),'launch','rsp.launch.py'
                )]),launch_arguments={'use_sim_time':"true"}.items()
    )

    #include the gz launch file, provided by the gazebo_ros package
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'),'launch','gz_sim.launch.py'
        )]),launch_arguments= {'gz_args': ['-r -v4 ',world]}.items()
    )

    #run the spawner node from the gazebo_ros pkg. the entity name doesnt matter if you only have one

    spawn_entity = Node(package="ros_gz_sim",executable="create",
                        arguments=['-topic','robot_description',
                                   '-name','my_bot',
                                   '-z','0.1'],
                        output= 'screen')

    #connects stuffs to the robot
    bridge_params = os.path.join(pkg_share, 'config', 'gz_bridge.yaml')

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}'
        ],
        output="screen"
    )


    #launch
    return LaunchDescription([
        world_arg,
        rsp,
        gazebo,
        spawn_entity,
        bridge
    ])