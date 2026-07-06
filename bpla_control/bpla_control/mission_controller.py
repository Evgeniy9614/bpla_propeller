#!/usr/bin/env python3
"""
Mission Controller — конечный автомат управления полётом.
Состояния: GROUND → TAKEOFF → HOVER → WAYPOINT → LAND → GROUND
"""
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
import time
import math
from enum import Enum


class State(Enum):
    GROUND = 0
    TAKEOFF = 1
    HOVER = 2
    WAYPOINT = 3
    LAND = 4


class MissionController(Node):
    def __init__(self):
        super().__init__('mission_controller')

        self.rpm_pub = self.create_publisher(PropellerCommand, '/propeller/cmd', 10)
        self.dt = 0.01
        self.timer = self.create_timer(self.dt, self.timer_callback)

        # Физика
        self.mass = 2.0
        self.weight = self.mass * 9.81
        self.k = 2.0e-5
        self.hover_rpm = math.sqrt(self.weight / (4.0 * self.k))
        self.max_rpm = 8000.0

        # Состояние дрона
        self.height = 0.0
        self.velocity = 0.0
        self.x = 0.0          # горизонтальная позиция (упрощённо)
        self.y = 0.0

        # === КОНЕЧНЫЙ АВТОМАТ ===
        self.state = State.GROUND
        self.state_start_time = time.time()
        self.target_height = 10.0

        # PID высоты
        self.Kp = 300.0
        self.Ki = 40.0
        self.Kd = 100.0
        self.error_sum = 0.0
        self.last_error = 0.0
        self.last_time = time.time()
        self.initialized = False

        # === МИССИЯ (список точек) ===
        self.waypoints = [
            (5.0, 0.0),    # вперёд на 5 м
            (5.0, 5.0),    # вправо на 5 м
            (0.0, 5.0),    # назад на 5 м
            (0.0, 0.0),    # вернуться домой
        ]
        self.current_waypoint = 0
        self.waypoint_tolerance = 0.5  # метров

        self.get_logger().info('Mission Controller started')
        self.get_logger().info(f'Initial state: {self.state.name}')

    def timer_callback(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if not self.initialized:
            self.initialized = True
            self.last_error = self.target_height - self.height
            return

        if dt <= 0 or dt > 0.05:
            dt = self.dt

        # === PID высоты ===
        error = self.target_height - self.height
        p_term = self.Kp * error
        self.error_sum += error * dt
        if self.error_sum * error < 0:
            self.error_sum = 0.0
        self.error_sum = max(-200, min(200, self.error_sum))
        i_term = self.Ki * self.error_sum
        error_rate = (error - self.last_error) / dt
        self.last_error = error
        d_term = self.Kd * error_rate

        rpm = self.hover_rpm + p_term + i_term + d_term
        rpm = max(0.0, min(rpm, self.max_rpm))

        # === КОНЕЧНЫЙ АВТОМАТ ===
        self.update_state(now)

        # === ДВИЖЕНИЕ К ТОЧКЕ ===
        if self.state == State.WAYPOINT:
            self.move_to_waypoint(dt)

        # Публикация RPM
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

        # Лог
        if int(now * 2) != int((now - dt) * 2):
            self.get_logger().info(
                f'[{self.state.name}] H={self.height:.2f}m '
                f'X={self.x:.1f} Y={self.y:.1f} | RPM={rpm:.0f}'
            )

    def update_state(self, now):
        """Логика переходов между состояниями"""
        elapsed = now - self.state_start_time

        if self.state == State.GROUND:
            # Автоматический взлёт через 2 секунды
            if elapsed > 2.0:
                self.state = State.TAKEOFF
                self.state_start_time = now
                self.target_height = 10.0
                self.get_logger().info('🚀 TAKEOFF!')

        elif self.state == State.TAKEOFF:
            # Взлетели на целевую высоту
            if abs(self.height - self.target_height) < 0.3 and abs(self.velocity) < 0.5:
                self.state = State.HOVER
                self.state_start_time = now
                self.get_logger().info('📍 HOVERING')

        elif self.state == State.HOVER:
            # Висим 3 секунды, потом летим по точкам
            if elapsed > 3.0 and self.waypoints:
                self.state = State.WAYPOINT
                self.state_start_time = now
                self.current_waypoint = 0
                self.get_logger().info(f'✈️ WAYPOINT {self.current_waypoint}: '
                                      f'{self.waypoints[0]}')

        elif self.state == State.WAYPOINT:
            # Прилетели в точку
            wp = self.waypoints[self.current_waypoint]
            dist = math.sqrt((self.x - wp[0])**2 + (self.y - wp[1])**2)
            if dist < self.waypoint_tolerance:
                self.current_waypoint += 1
                if self.current_waypoint >= len(self.waypoints):
                    self.state = State.LAND
                    self.state_start_time = now
                    self.target_height = 0.0
                    self.get_logger().info('🛬 LANDING')
                else:
                    self.get_logger().info(f'✈️ WAYPOINT {self.current_waypoint}: '
                                          f'{self.waypoints[self.current_waypoint]}')

        elif self.state == State.LAND:
            # Приземлились
            if self.height < 0.1:
                self.state = State.GROUND
                self.state_start_time = now
                self.get_logger().info('✅ MISSION COMPLETE')

    def move_to_waypoint(self, dt):
        """Упрощённое движение к точке (без PID по X/Y)"""
        if self.current_waypoint < len(self.waypoints):
            wp = self.waypoints[self.current_waypoint]
            dx = wp[0] - self.x
            dy = wp[1] - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0.1:
                speed = 2.0  # м/с
                self.x += (dx / dist) * speed * dt
                self.y += (dy / dist) * speed * dt


def main(args=None):
    rclpy.init(args=args)
    node = MissionController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
