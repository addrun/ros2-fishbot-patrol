from setuptools import find_packages, setup

package_name = 'fishbot_application'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='addrun',
    maintainer_email='141168900+addrun@users.noreply.github.com',
    description='Small Nav2 and TF application examples for FishBot.',
    license='Apache-2.0',
    # 
    entry_points={
        'console_scripts': [
            'init_robot_pose = fishbot_application.init_robot_pose:main',
            'get_robot_pose = fishbot_application.get_robot_pose:main',
            'nav_to_pose = fishbot_application.nav_to_pose:main',
            'waypoint_follower = fishbot_application.waypoint_follower:main',
        ],
    },
)
