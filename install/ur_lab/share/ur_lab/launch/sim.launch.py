import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    world = os.path.join(
        get_package_share_directory('ur_lab'),
        'worlds',
        'lab.world'
    )

    ur_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ur_simulation_gazebo'),
                'launch',
                'ur_sim_control.launch.py'
            )
        ),
        launch_arguments={
            'ur_type': 'ur5e',
            'world': world,
            'launch_rviz': 'false'
        }.items()
    )

    return LaunchDescription([
        ur_sim
    ])
