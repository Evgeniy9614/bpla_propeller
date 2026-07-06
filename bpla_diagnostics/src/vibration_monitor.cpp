#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <bpla_propeller_msgs/msg/propeller_command.hpp>
#include <std_msgs/msg/float32_multi_array.hpp>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>

class VibrationMonitor : public rclcpp::Node
{
public:
    VibrationMonitor()
    : Node("vibration_monitor")
    {
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "/imu/data_raw", 10,
            std::bind(&VibrationMonitor::imu_callback, this, std::placeholders::_1));

        rpm_sub_ = this->create_subscription<bpla_propeller_msgs::msg::PropellerCommand>(
            "/propeller/cmd", 10,
            std::bind(&VibrationMonitor::rpm_callback, this, std::placeholders::_1));

        this->declare_parameter("warning_threshold", 0.3);
        warning_threshold_ = this->get_parameter("warning_threshold").as_double();

        sample_rate_ = 1000.0;
        fft_size_ = 1024;
        buffer_.resize(fft_size_, 0.0f);
        buffer_index_ = 0;
        current_rpm_ = 0.0;

        timer_ = this->create_wall_timer(
            std::chrono::seconds(1),
            std::bind(&VibrationMonitor::analysis_callback, this));

        RCLCPP_INFO(this->get_logger(),
            "Vibration Monitor | Threshold=%.2f g", warning_threshold_);
    }

private:
    void imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        float mag = std::sqrt(
            msg->linear_acceleration.x * msg->linear_acceleration.x +
            msg->linear_acceleration.y * msg->linear_acceleration.y +
            msg->linear_acceleration.z * msg->linear_acceleration.z);
        buffer_[buffer_index_] = mag;
        buffer_index_ = (buffer_index_ + 1) % fft_size_;
    }

    void rpm_callback(const bpla_propeller_msgs::msg::PropellerCommand::SharedPtr msg)
    {
        current_rpm_ = msg->rpm;
    }

    void analysis_callback()
    {
        if (current_rpm_ < 100.0) return;

        float fundamental_freq = current_rpm_ / 60.0f;
        float freq_resolution = sample_rate_ / fft_size_;

        // Вычитаем среднее (убираем DC)
        float mean = std::accumulate(buffer_.begin(), buffer_.end(), 0.0f) / fft_size_;
        std::vector<float> centered(fft_size_);
        for (int i = 0; i < fft_size_; i++)
            centered[i] = buffer_[i] - mean;

        // FFT
        std::vector<float> spectrum(fft_size_ / 2, 0.0f);
        for (int k = 0; k < fft_size_ / 2; k++)
        {
            float real = 0.0f, imag = 0.0f;
            for (int n = 0; n < fft_size_; n++)
            {
                float angle = -2.0f * M_PI * k * n / fft_size_;
                real += centered[n] * std::cos(angle);
                imag += centered[n] * std::sin(angle);
            }
            spectrum[k] = std::sqrt(real*real + imag*imag) / fft_size_;
        }

        // Ищем максимум в окрестности фундаментальной частоты
        int target_bin = static_cast<int>(fundamental_freq / freq_resolution);
        float local_max = 0.0f;
        int peak_bin = 0;

        for (int b = std::max(1, target_bin - 3); b <= std::min(fft_size_/2 - 1, target_bin + 3); b++)
        {
            if (spectrum[b] > local_max)
            {
                local_max = spectrum[b];
                peak_bin = b;
            }
        }

        if (local_max > warning_threshold_)
        {
            RCLCPP_WARN(this->get_logger(),
                "⚠️ HIGH VIBRATION at %.1f Hz (bin %d)! Amplitude=%.3f g",
                peak_bin * freq_resolution, peak_bin, local_max);
        }

        RCLCPP_INFO(this->get_logger(),
            "RPM=%.0f Freq=%.1f Hz | Bin=%d Local=%.3f g | %s",
            current_rpm_, fundamental_freq, target_bin, local_max,
            local_max > warning_threshold_ ? "⚠️ WARNING" : "OK");
    }

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<bpla_propeller_msgs::msg::PropellerCommand>::SharedPtr rpm_sub_;
    rclcpp::Publisher<std_msgs::msg::Float32MultiArray>::SharedPtr spectrum_pub_;
    rclcpp::TimerBase::SharedPtr timer_;

    double sample_rate_, warning_threshold_;
    int fft_size_;
    std::vector<float> buffer_;
    int buffer_index_;
    float current_rpm_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<VibrationMonitor>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
