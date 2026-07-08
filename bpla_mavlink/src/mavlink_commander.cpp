#include <rclcpp/rclcpp.hpp>
#include <bpla_propeller_msgs/msg/propeller_command.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <cmath>

/**
 * @brief Симуляция MAVLink-команд для автопилота.
 * 
 * Эта нода демонстрирует, как наземная станция (GCS)
 * отправляет команды полётному контроллеру через MAVLink.
 * 
 * Поддерживаемые команды:
 * - TAKEOFF: взлёт на заданную высоту
 * - LAND: посадка
 * - GOTO: полёт к точке (x, y, z)
 * - RTL: возврат домой (Return To Launch)
 */
class MAVLinkCommander : public rclcpp::Node
{
public:
    MAVLinkCommander()
    : Node("mavlink_commander")
    {
        // Публикация команд RPM (для наших нод)
        rpm_pub_ = this->create_publisher<bpla_propeller_msgs::msg::PropellerCommand>(
            "/propeller/cmd", 10);
        
        // Публикация целевой позиции (MAVLink SET_POSITION_TARGET)
        setpoint_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
            "/mavlink/setpoint", 10);
        
        // Таймер выполнения команд
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(&MAVLinkCommander::timer_callback, this));
        
        // Параметры MAVLink
        this->declare_parameter("takeoff_altitude", 10.0);
        this->declare_parameter("rtl_altitude", 15.0);
        
        takeoff_altitude_ = this->get_parameter("takeoff_altitude").as_double();
        rtl_altitude_ = this->get_parameter("rtl_altitude").as_double();
        
        current_command_ = "NONE";
        home_x_ = 0.0;
        home_y_ = 0.0;
        current_x_ = 0.0;
        current_y_ = 0.0;
        current_z_ = 0.0;
        
        RCLCPP_INFO(this->get_logger(),
            "MAVLink Commander ready. Home: (%.1f, %.1f). Takeoff alt: %.1f m",
            home_x_, home_y_, takeoff_altitude_);
    }
    
private:
    void timer_callback()
    {
        // В реальном MAVLink здесь была бы очередь команд
        // и конечный автомат состояний полёта
        auto rpm_msg = bpla_propeller_msgs::msg::PropellerCommand();
        rpm_msg.rpm = 0.0;
        rpm_msg.motor_name = "all";
        rpm_pub_->publish(rpm_msg);
    }
    
    /**
     * @brief MAVLink команда взлёта
     * @param altitude высота в метрах
     */
    void cmd_takeoff(double altitude)
    {
        current_command_ = "TAKEOFF";
        
        auto setpoint = geometry_msgs::msg::PoseStamped();
        setpoint.header.stamp = this->now();
        setpoint.pose.position.z = altitude;
        setpoint_pub_->publish(setpoint);
        
        RCLCPP_INFO(this->get_logger(),
            "MAVLink CMD: TAKEOFF to %.1f m", altitude);
    }
    
    /**
     * @brief MAVLink команда полёта к точке
     * @param x, y координаты в локальной системе NED
     * @param z высота (отрицательная вниз в NED!)
     */
    void cmd_goto(double x, double y, double z)
    {
        current_command_ = "GOTO";
        
        auto setpoint = geometry_msgs::msg::PoseStamped();
        setpoint.header.stamp = this->now();
        setpoint.pose.position.x = x;
        setpoint.pose.position.y = y;
        setpoint.pose.position.z = z;
        setpoint_pub_->publish(setpoint);
        
        RCLCPP_INFO(this->get_logger(),
            "MAVLink CMD: GOTO (%.1f, %.1f, %.1f)", x, y, z);
    }
    
    /**
     * @brief MAVLink команда возврата домой (RTL)
     */
    void cmd_rtl()
    {
        current_command_ = "RTL";
        
        auto setpoint = geometry_msgs::msg::PoseStamped();
        setpoint.header.stamp = this->now();
        setpoint.pose.position.x = home_x_;
        setpoint.pose.position.y = home_y_;
        setpoint.pose.position.z = rtl_altitude_;
        setpoint_pub_->publish(setpoint);
        
        RCLCPP_INFO(this->get_logger(),
            "MAVLink CMD: RTL to (%.1f, %.1f, %.1f m)",
            home_x_, home_y_, rtl_altitude_);
    }
    
    /**
     * @brief MAVLink команда посадки
     */
    void cmd_land()
    {
        current_command_ = "LAND";
        
        auto setpoint = geometry_msgs::msg::PoseStamped();
        setpoint.header.stamp = this->now();
        setpoint.pose.position.z = 0.0;
        setpoint_pub_->publish(setpoint);
        
        RCLCPP_INFO(this->get_logger(), "MAVLink CMD: LAND");
    }
    
    rclcpp::Publisher<bpla_propeller_msgs::msg::PropellerCommand>::SharedPtr rpm_pub_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr setpoint_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    
    double takeoff_altitude_, rtl_altitude_;
    double home_x_, home_y_, current_x_, current_y_, current_z_;
    std::string current_command_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<MAVLinkCommander>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
