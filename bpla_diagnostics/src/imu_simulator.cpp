#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <bpla_propeller_msgs/msg/propeller_command.hpp>
#include <cmath>
#include <random>

class IMUSimulator : public rclcpp::Node
{
public:
    IMUSimulator()
    : Node("imu_simulator")
    {
        publisher_ = this->create_publisher<sensor_msgs::msg::Imu>("/imu/data_raw", 10);

        rpm_sub_ = this->create_subscription<bpla_propeller_msgs::msg::PropellerCommand>(
            "/propeller/cmd", 10,
            std::bind(&IMUSimulator::rpm_callback, this, std::placeholders::_1)
        );

        // Таймер 1000 Гц
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(1),
            std::bind(&IMUSimulator::timer_callback, this)
        );

        current_rpm_ = 0.0;
        time_ = 0.0;
        gen_ = std::mt19937(rd_());
        noise_ = std::normal_distribution<float>(0.0f, 0.02f);

        RCLCPP_INFO(this->get_logger(), "IMU Simulator started at 1000 Hz");
    }

private:
    void rpm_callback(const bpla_propeller_msgs::msg::PropellerCommand::SharedPtr msg)
    {
        current_rpm_ = msg->rpm;
    }

    void timer_callback()
    {
        auto msg = sensor_msgs::msg::Imu();
        msg.header.stamp = this->now();
        msg.header.frame_id = "imu_link";

        if (current_rpm_ > 100.0f)
        {
            float freq = current_rpm_ / 60.0f;  // RPM → Гц
            float omega = 2.0f * M_PI * freq;

            // Основная вибрация (1x частота вращения — дисбаланс)
            float vibration = 50.0f * std::sin(omega * time_);

            // 2x гармоника (износ подшипника)
            vibration += 3.0f * std::sin(2.0f * omega * time_);

            // 3x гармоника (лопастная частота)
            vibration += 0.05f * std::sin(3.0f * omega * time_);

            // Шум
            vibration += noise_(gen_);

            msg.linear_acceleration.x = vibration;
            msg.linear_acceleration.y = noise_(gen_);
            msg.linear_acceleration.z = noise_(gen_);
        }
        else
        {
            msg.linear_acceleration.x = noise_(gen_);
            msg.linear_acceleration.y = noise_(gen_);
            msg.linear_acceleration.z = noise_(gen_);
        }

        publisher_->publish(msg);
        time_ += 0.001;  // 1 мс
    }

    rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr publisher_;
    rclcpp::Subscription<bpla_propeller_msgs::msg::PropellerCommand>::SharedPtr rpm_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    float current_rpm_;
    float time_;
    std::random_device rd_;
    std::mt19937 gen_;
    std::normal_distribution<float> noise_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<IMUSimulator>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
