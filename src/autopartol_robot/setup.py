from setuptools import find_packages, setup
from glob import glob
package_name = 'autopartol_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob('launch/*.launch.py')),
        ('share/' + package_name + '/config', glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    extras_require={'test': ['pytest']},
    zip_safe=True,
    maintainer='addrun',
    maintainer_email='141168900+addrun@users.noreply.github.com',
    description='Waypoint patrol, image recording and optional speech for FishBot.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'patrol_node = autopartol_robot.partol_node:main',
            'speaker = autopartol_robot.speaker:main',
            'speaker_tts = autopartol_robot.speaker_tts:main',
            
        ],
    },
)
