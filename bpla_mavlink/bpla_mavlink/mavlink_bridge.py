#!/usr/bin/env python3
"""
Мост между ROS 2 и MAVLink (протокол Pixhawk/PX4).
Принимает PropellerCommand и конвертирует в MAVLink-команды.
"""
import rclpy
from rclpy.node import Node
from bpla_propeller_msgs.msg import PropellerCommand
from geometry_msgs.msg import PoseStamped, TwistStamped
import struct
import time


class MAVLinkBridge(Node):
    """
    Симуляция MAVLink-соединения с полётным контроллером.
    
    MAVLink — стандартный протокол связи с автопилотами
    (Pixhawk, PX4, ArduPilot). Используется для:
    - Команд управления (SET_POSITION, SET_ATTITUDE)
    - Телеметрии (HEARTBEAT, ATTITUDE, BATTERY_STATUS)
    - Параметров (PARAM_REQUEST, PARAM_SET)
    """
    
    # MAVLink message IDs (реальные номера из протокола)
    MAVLINK_MSG_ID_HEARTBEAT = 0
    MAVLINK_MSG_ID_ATTITUDE = 30
    MAVLINK_MSG_ID_GLOBAL_POSITION = 33
    MAVLINK_MSG_ID_SET_POSITION_TARGET_LOCAL_NED = 84
    MAVLINK_MSG_ID_COMMAND_LONG = 76
    MAVLINK_MSG_ID_BATTERY_STATUS = 147
    
    # MAVLink компоненты
    MAV_COMP_ID_AUTOPILOT = 1
    MAV_COMP_ID_GCS = 195  # Ground Control Station
    
    # MAVLink команды
    MAV_CMD_TAKEOFF = 22
    MAV_CMD_LAND = 21
    MAV_CMD_NAV_WAYPOINT = 16
    
    def __init__(self):
        super().__init__('mavlink_bridge')
        
        # Subscriber: команды RPM из наших нод
        self.rpm_sub = self.create_subscription(
            PropellerCommand, '/propeller/cmd',
            self.rpm_callback, 10)
        
        # Publisher: позиция (как MAVLink GLOBAL_POSITION_INT)
        self.pos_pub = self.create_publisher(
            PoseStamped, '/mavlink/position', 10)
        
        # Publisher: команды управления (как MAVLink SET_POSITION)
        self.cmd_pub = self.create_publisher(
            PoseStamped, '/mavlink/setpoint', 10)
        
        # Publisher: статус батареи (как MAVLink BATTERY_STATUS)
        self.battery_pub = self.create_publisher(
            TwistStamped, '/mavlink/battery', 10)
        
        # Таймер HEARTBEAT (1 Hz — как в реальном MAVLink)
        self.heartbeat_timer = self.create_timer(1.0, self.heartbeat_callback)
        
        # Состояние
        self.current_rpm = 0.0
        self.battery_voltage = 12.6  # 3S LiPo
        self.flight_mode = "STABILIZE"
        self.armed = False
        self.last_heartbeat = time.time()
        
        self.get_logger().info('MAVLink Bridge started (simulated Pixhawk connection)')
        self.get_logger().info('Flight mode: STABILIZE | Armed: False')
    
    def rpm_callback(self, msg):
        """Принимаем RPM и обновляем телеметрию"""
        self.current_rpm = msg.rpm
        
        if self.current_rpm > 100 and not self.armed:
            self.armed = True
            self.flight_mode = "GUIDED"
            self.get_logger().info('🚀 Armed! Flight mode: GUIDED')
    
    def heartbeat_callback(self):
        """
        MAVLink HEARTBEAT — обязательное сообщение.
        Отправляется каждую секунду, чтобы GCS знала,
        что полётный контроллер жив.
        
        Тип: MAV_TYPE_QUADROTOR (2)
        Автопилот: MAV_AUTOPILOT_PX4 (12)
        Режим: GUIDED (4)
        """
        self.last_heartbeat = time.time()
        
        # В реальном MAVLink это был бы бинарный пакет
        # Здесь просто публикуем позицию как доказательство жизни
        pose = PoseStamped()
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.header.frame_id = "world"
        pose.pose.position.z = 0.0  # на земле
        self.pos_pub.publish(pose)
    
    def send_takeoff(self, altitude: float = 10.0):
        """
        MAVLink команда: MAV_CMD_NAV_TAKEOFF
        Отправляет команду взлёта на заданную высоту.
        
        Параметры:
        - param7: высота (метры)
        """
        cmd = PoseStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.pose.position.z = altitude
        self.cmd_pub.publish(cmd)
        self.get_logger().info(f'✈️ MAVLink TAKEOFF command: {altitude}m')
    
    def send_land(self):
        """
        MAVLink команда: MAV_CMD_NAV_LAND
        Отправляет команду посадки.
        """
        cmd = PoseStamped()
        cmd.header.stamp = self.get_clock().now().to_msg()
        cmd.pose.position.z = 0.0
        self.cmd_pub.publish(cmd)
        self.get_logger().info('🛬 MAVLink LAND command')
    
    def get_battery_status(self):
        """MAVLink BATTERY_STATUS"""
        return self.battery_voltage


def main(args=None):
    rclpy.init(args=args)
    node = MAVLinkBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
