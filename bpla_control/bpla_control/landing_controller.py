#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
import numpy as np
import time
import math

class LandingController(Node):
    def __init__(self):
        super().__init__('landing_controller')
        self.rpm_pub = self.create_publisher(PropellerCommand, '/propeller/cmd', 10)
        self.dt = 0.1
        self.timer = self.create_timer(self.dt, self.timer_callback)

        self.mass = 2.0
        self.weight = self.mass * 9.81
        self.k = 2.0e-5
        self.hover_rpm = math.sqrt(self.weight / (4.0 * self.k))
        self.max_rpm = 8000.0

        self.height = 10.0
        self.velocity_z = 0.0
        self.x = 0.0
        self.y = 0.0

        self.target_height = 10.0
        self.Kp_z = 200.0
        self.Ki_z = 30.0
        self.Kd_z = 80.0
        self.error_sum_z = 0.0
        self.last_error_z = 0.0

        self.tag_x = 2.0
        self.tag_y = 3.0
        self.phase = "SEARCH"
        self.phase_start = time.time()
        self.last_time = time.time()
        self.initialized = False

        self.get_logger().info(f'Landing Controller | Tag at ({self.tag_x}, {self.tag_y})')

    def timer_callback(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now
        if not self.initialized:
            self.initialized = True
            return
        if dt <= 0 or dt > 0.2:
            dt = self.dt

        elapsed = now - self.phase_start

        # Фазы
        if self.phase == "SEARCH" and elapsed > 3.0:
            self.phase = "APPROACH"
            self.phase_start = now
            self.get_logger().info(f'📍 APPROACH | X={self.x:.2f} Y={self.y:.2f}')

        elif self.phase == "APPROACH":
            self.target_height = max(2.0, self.target_height - 0.03)
            dist = math.sqrt((self.x - self.tag_x)**2 + (self.y - self.tag_y)**2)
            if dist < 0.5 and self.height < 5.0:
                self.phase = "LAND"
                self.phase_start = now
                self.target_height = 0.0
                self.get_logger().info(f'🛬 LANDING | Dist to tag: {dist:.2f}m')

        elif self.phase == "LAND" and self.height < 0.1:
            self.phase = "DONE"
            self.get_logger().info(f'✅ LANDED! Final pos: X={self.x:.2f} Y={self.y:.2f}')

        # PID высоты
        error_z = self.target_height - self.height
        p_z = self.Kp_z * error_z
        self.error_sum_z += error_z * dt
        self.error_sum_z = max(-200, min(200, self.error_sum_z))
        i_z = self.Ki_z * self.error_sum_z
        d_z = self.Kd_z * (error_z - self.last_error_z) / dt if dt > 0 else 0
        self.last_error_z = error_z
        rpm = self.hover_rpm + p_z + i_z + d_z
        rpm = max(0.0, min(rpm, self.max_rpm))

        msg = PropellerCommand()
        msg.rpm = rpm
        msg.motor_name = 'all'
        self.rpm_pub.publish(msg)

        # Физика
        thrust = 4.0 * self.k * rpm * rpm
        acc_z = (thrust - self.weight) / self.mass
        self.velocity_z += acc_z * dt
        self.height += self.velocity_z * dt
        if self.height < 0.0:
            self.height = 0.0
            self.velocity_z = 0.0

        # Горизонтальное движение (упрощённое, прямое)
        if self.phase in ["APPROACH", "LAND"]:
            dx = self.tag_x - self.x
            dy = self.tag_y - self.y
            speed = 0.5  # м/с
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0.05:
                self.x += (dx / dist) * speed * dt
                self.y += (dy / dist) * speed * dt

        # Лог
        if int(now * 2) != int((now - dt) * 2):
            dist = math.sqrt((self.x - self.tag_x)**2 + (self.y - self.tag_y)**2)
            self.get_logger().info(
                f'[{self.phase}] H={self.height:.2f}m '
                f'X={self.x:.2f} Y={self.y:.2f} | '
                f'Dist={dist:.2f}m | RPM={rpm:.0f}')

def main(args=None):
    rclpy.init(args=args)
    node = LandingController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
