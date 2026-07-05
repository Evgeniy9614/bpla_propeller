#!/usr/bin/env python3
"""
Мост между PropellerCommand (RPM) и joint_states (углы пропеллеров).
Публикует ВСЕ joint'ы, чтобы robot_state_publisher строил полное TF-дерево.
"""
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
from sensor_msgs.msg import JointState
import math
import time

class PropellerJointBridge(Node):
    def __init__(self):
        super().__init__('propeller_joint_bridge')

        self.subscription = self.create_subscription(
            PropellerCommand, '/propeller/cmd', self.command_callback, 10)
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)
        self.timer = self.create_timer(0.01, self.timer_callback)

        self.rpm = 0.0
        self.angle = 0.0
        self.last_command_time = time.time()

        # ВСЕ joint'ы из URDF (fixed всегда 0.0, continuous вычисляются)
        self.joint_names = [
            'arm_1_joint', 'arm_2_joint', 'arm_3_joint', 'arm_4_joint',
            'motor_1_joint', 'motor_2_joint', 'motor_3_joint', 'motor_4_joint',
            'prop_1_joint', 'prop_2_joint', 'prop_3_joint', 'prop_4_joint'
        ]

        self.get_logger().info('Propeller Joint Bridge started')

    def command_callback(self, msg):
        self.rpm = msg.rpm
        self.last_command_time = time.time()

    def timer_callback(self):
        if time.time() - self.last_command_time > 0.5:
            self.rpm = 0.0

        dt = 0.01
        angular_velocity = self.rpm * 2.0 * math.pi / 60.0
        self.angle += angular_velocity * dt

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = self.joint_names
        
        # 8 fixed joints = 0.0, 4 continuous = angle (одинаковый для всех)
        msg.position = [0.0]*8 + [self.angle]*4
        msg.velocity = [0.0]*8 + [angular_velocity]*4
        msg.effort = [0.0]*12

        self.joint_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PropellerJointBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
