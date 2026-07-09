#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
from visualization_msgs.msg import Marker, MarkerArray
from geometry_msgs.msg import Point
import math
import time

class PropellerViz(Node):
    def __init__(self):
        super().__init__('propeller_viz')
        self.subscription = self.create_subscription(
            PropellerCommand, '/propeller/cmd', self.command_callback, 10)
        self.marker_pub = self.create_publisher(MarkerArray, '/propeller/markers', 10)
        self.timer = self.create_timer(0.033, self.timer_callback)
        self.rpm = 0.0
        self.angle = 0.0
        self.blade_length = 1.0
        self.blade_width = 0.08
        self.hub_radius = 0.15
        self.last_command_time = time.time()
        self.get_logger().info('Propeller Visualization started')

    def command_callback(self, msg):
        self.rpm = msg.rpm
        self.last_command_time = time.time()

    def timer_callback(self):
        # Если команд нет больше 0.5 секунды — сбрасываем RPM в 0
        if time.time() - self.last_command_time > 0.5:
            self.rpm = 0.0
        
        angular_velocity = self.rpm * 2.0 * math.pi / 60.0
        self.angle += angular_velocity * 0.033
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi
        self.marker_pub.publish(self.create_markers())

    def create_markers(self):
        marker_array = MarkerArray()
        
        hub = Marker()
        hub.header.frame_id = "world"
        hub.header.stamp = self.get_clock().now().to_msg()
        hub.ns = "propeller"
        hub.id = 0
        hub.type = Marker.CYLINDER
        hub.action = Marker.ADD
        hub.pose.position.z = 0.0
        hub.scale.x = self.hub_radius * 2
        hub.scale.y = self.hub_radius * 2
        hub.scale.z = 0.06
        hub.color.r = 0.3
        hub.color.g = 0.3
        hub.color.b = 0.3
        hub.color.a = 1.0
        marker_array.markers.append(hub)

        for i, offset in enumerate([0.0, math.pi]):
            a = self.angle + offset
            tip_x = self.blade_length * math.cos(a)
            tip_y = self.blade_length * math.sin(a)
            base_x = self.hub_radius * math.cos(a)
            base_y = self.hub_radius * math.sin(a)

            blade = Marker()
            blade.header.frame_id = "world"
            blade.header.stamp = self.get_clock().now().to_msg()
            blade.ns = "propeller"
            blade.id = i + 1
            blade.type = Marker.LINE_STRIP
            blade.action = Marker.ADD
            blade.scale.x = self.blade_width
            
            # Плавный цвет по RPM (зелёный → жёлтый → красный)
            ratio = min(self.rpm / 1500.0, 1.0)
            blade.color.r = ratio
            blade.color.g = 1.0 - ratio
            self.get_logger().info(f"RPM={self.rpm:.0f} ratio={ratio:.2f} r={blade.color.r:.2f} g={blade.color.g:.2f}")
            blade.color.b = 0.0
            
            blade.color.a = 1.0
            
            p1 = Point()
            p1.x = base_x
            p1.y = base_y
            p1.z = 0.0
            
            p2 = Point()
            p2.x = tip_x
            p2.y = tip_y
            p2.z = 0.0
            
            blade.points = [p1, p2]
            marker_array.markers.append(blade)

        return marker_array

def main(args=None):
    rclpy.init(args=args)
    node = PropellerViz()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
