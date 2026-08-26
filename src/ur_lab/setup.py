from setuptools import setup

package_name = 'ur_lab'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='user',
    maintainer_email='user@todo.todo',
    description='UR5e pushing lab',
    license='Apache License 2.0',

    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name,
            ['package.xml']),

        ('share/' + package_name + '/launch',
            ['launch/sim.launch.py']),

        ('share/' + package_name + '/worlds',
            ['worlds/lab.world']),

        ('share/' + package_name + '/config',
            ['config/ur_controllers.yaml']),

        ('share/' + package_name + '/urdf',
            ['urdf/ur5e_gripper.urdf.xacro']),
    ],

    entry_points={
        'console_scripts': [
        'add_scene = ur_lab.add_scene:main',
        'move_robot = ur_lab.move_robot:main',
        'pick_cube = ur_lab.pick_cube:main',
        ],
    },
)

