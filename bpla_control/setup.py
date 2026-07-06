from setuptools import find_packages, setup

package_name = 'bpla_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email@example.com',
    description='BPLA Control',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'hover_controller = bpla_control.hover_controller:main',
            'mission_controller = bpla_control.mission_controller:main',
            'landing_controller = bpla_control.landing_controller:main',
        ],
    },
)
