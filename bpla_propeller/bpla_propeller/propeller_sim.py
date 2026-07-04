#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
import math

class PropellerSim(Node):
    def __init__(self):
        super().__init__('propeller_sim')
        self.publisher_ = self.create_publisher(PropellerCommand, '/propeller/cmd', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.time = 0.0
        self.get_logger().info('Propeller Simulator started')

    def timer_callback(self):
        msg = PropellerCommand()
        msg.rpm = 1000.0 + 200.0 * math.sin(self.time * 0.5)
        msg.motor_name = "main_rotor"
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.motor_name} -> {msg.rpm:.1f} RPM')
        self.time += 0.1

def main(args=None):
    rclpy.init(args=args)
    node = PropellerSim()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
