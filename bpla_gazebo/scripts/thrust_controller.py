#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
from gazebo_msgs.srv import ApplyLinkWrench
import time

class ThrustController(Node):
    def __init__(self):
        super().__init__('thrust_controller')
        self.wrench_client = self.create_client(ApplyLinkWrench, '/apply_link_wrench')
        self.get_logger().info('Waiting for /apply_link_wrench...')
        if not self.wrench_client.wait_for_service(timeout_sec=10.0):
            self.get_logger().error('Service not available!')
            return
        self.get_logger().info('Service available!')

        self.subscription = self.create_subscription(
            PropellerCommand, '/propeller/cmd', self.command_callback, 10)
        self.timer = self.create_timer(0.01, self.timer_callback)

        self.rpm = 0.0
        self.last_cmd_time = time.time()
        self.k = 2.0e-5
        self.max_rpm = 10000.0

        # Пробуем разные варианты имён
        self.motor_links = [
            'motor_1', 'motor_2', 'motor_3', 'motor_4',
            'quadcopter::motor_1', 'quadcopter::motor_2',
            'quadcopter::motor_3', 'quadcopter::motor_4'
        ]

        self.get_logger().info('Thrust Controller started')

    def command_callback(self, msg):
        self.rpm = msg.rpm
        self.last_cmd_time = time.time()

    def timer_callback(self):
        if time.time() - self.last_cmd_time > 0.5:
            self.rpm = 0.0

        rpm = min(self.rpm, self.max_rpm)
        thrust = self.k * rpm * rpm

        for link_name in self.motor_links:
            req = ApplyLinkWrench.Request()
            req.link_name = link_name
            req.wrench.force.z = thrust
            req.duration.sec = 0
            req.duration.nanosec = 20000000
            self.wrench_client.call_async(req)

        if rpm > 100:
            self.get_logger().info(f'RPM: {rpm:.0f}, Thrust: {thrust:.1f} N',
                                  throttle_duration_sec=1.0)

def main(args=None):
    rclpy.init(args=args)
    node = ThrustController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
