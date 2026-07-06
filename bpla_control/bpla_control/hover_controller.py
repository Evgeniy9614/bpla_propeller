#!/usr/bin/env python3
"""
PID-регулятор высоты с математической моделью дрона.
"""
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
import time
import math


class HoverController(Node):
    def __init__(self):
        super().__init__('hover_controller')

        self.rpm_pub = self.create_publisher(PropellerCommand, '/propeller/cmd', 10)
        self.dt = 0.01
        self.timer = self.create_timer(self.dt, self.timer_callback)

        # Физика
        self.mass = 2.0
        self.weight = self.mass * 9.81
        self.k = 2.0e-5
        self.hover_rpm = math.sqrt(self.weight / (4.0 * self.k))
        self.max_rpm = 8000.0

        # Состояние
        self.height = 0.0
        self.velocity = 0.0

        # PID
        self.Kp = 300.0
        self.Ki = 40.0
        self.Kd = 100.0

        self.target_height = 10.0
        self.error_sum = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        self.initialized = False  # флаг первого запуска

        self.get_logger().info(f'Hover Controller | Target: {self.target_height}m | '
                               f'Hover RPM: {self.hover_rpm:.0f}')

    def timer_callback(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # Игнорируем первый вызов (dt может быть огромным)
        if not self.initialized:
            self.initialized = True
            self.last_error = self.target_height - self.height
            return

        # Ограничиваем dt
        if dt <= 0 or dt > 0.05:
            dt = self.dt

        # Ошибка
        error = self.target_height - self.height

        # P
        p_term = self.Kp * error

        # I
        self.error_sum += error * dt
        if self.error_sum * error < 0:
            self.error_sum = 0.0
        self.error_sum = max(-200, min(200, self.error_sum))
        i_term = self.Ki * self.error_sum

        # D
        error_rate = (error - self.last_error) / dt
        self.last_error = error
        d_term = self.Kd * error_rate

        # RPM
        rpm = self.hover_rpm + p_term + i_term + d_term
        rpm = max(0.0, min(rpm, self.max_rpm))

        # Публикация
        msg = PropellerCommand()
        msg.rpm = rpm
        msg.motor_name = 'all'
        self.rpm_pub.publish(msg)

        # Физика
        thrust_per_motor = self.k * rpm * rpm
        total_thrust = 4.0 * thrust_per_motor
        net_force = total_thrust - self.weight
        acceleration = net_force / self.mass
        self.velocity += acceleration * dt
        self.height += self.velocity * dt
        if self.height < 0.0:
            self.height = 0.0
            if self.velocity < 0.0:
                self.velocity = 0.0

        # Лог (каждые 0.5 сек)
        if int(now * 2) != int((now - dt) * 2):
            self.get_logger().info(
                f'H={self.height:.2f}m | Err={error:.2f} | '
                f'P={p_term:.0f} I={i_term:.0f} D={d_term:.0f} | '
                f'RPM={rpm:.0f} | V={self.velocity:.2f} m/s'
            )


def main(args=None):
    rclpy.init(args=args)
    node = HoverController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
