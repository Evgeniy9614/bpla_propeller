#include <rclcpp/rclcpp.hpp>
#include <bpla_propeller_msgs/msg/propeller_command.hpp>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <cstring>
#include <sstream>
#include <thread>
#include <atomic>

class RMSServer : public rclcpp::Node
{
public:
    RMSServer() : Node("rms_server"), running_(true)
    {
        rpm_pub_ = this->create_publisher<bpla_propeller_msgs::msg::PropellerCommand>("/propeller/cmd", 10);
        this->declare_parameter("port", 8080);
        port_ = this->get_parameter("port").as_int();
        server_thread_ = std::thread(&RMSServer::run_server, this);
        RCLCPP_INFO(this->get_logger(), "RMS Server started on port %d", port_);
    }
    ~RMSServer()
    {
        running_ = false;
        if (server_fd_ >= 0) close(server_fd_);
        if (server_thread_.joinable()) server_thread_.join();
    }
private:
    void run_server()
    {
        server_fd_ = socket(AF_INET, SOCK_STREAM, 0);
        int opt = 1;
        setsockopt(server_fd_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);
        bind(server_fd_, (sockaddr*)&addr, sizeof(addr));
        listen(server_fd_, 5);
        RCLCPP_INFO(this->get_logger(), "Waiting for connections...");
        while (running_)
        {
            int client = accept(server_fd_, nullptr, nullptr);
            if (client < 0) continue;
            RCLCPP_INFO(this->get_logger(), "Client connected");
            handle_client(client);
            close(client);
        }
    }
    void handle_client(int client)
    {
        char buffer[1024];
        while (running_)
        {
            int n = recv(client, buffer, sizeof(buffer)-1, 0);
            if (n <= 0) break;
            buffer[n] = '\0';
            std::string response = process_command(std::string(buffer));
            send(client, response.c_str(), response.size(), 0);
        }
    }
    std::string process_command(const std::string& cmd)
    {
        auto msg = bpla_propeller_msgs::msg::PropellerCommand();
        std::stringstream ss(cmd);
        std::string action;
        ss >> action;
        if (action == "TAKEOFF") { msg.rpm = 3500.0; msg.motor_name = "all"; rpm_pub_->publish(msg); return "OK TAKEOFF\n"; }
        if (action == "LAND") { msg.rpm = 0.0; msg.motor_name = "all"; rpm_pub_->publish(msg); return "OK LAND\n"; }
        if (action == "RPM") { double r; if (ss >> r) { msg.rpm = r; msg.motor_name = "all"; rpm_pub_->publish(msg); return "OK RPM " + std::to_string(r) + "\n"; } }
        if (action == "STATUS") return "STATUS: armed=true, mode=GUIDED, battery=12.6V\n";
        return "ERROR\n";
    }
    rclcpp::Publisher<bpla_propeller_msgs::msg::PropellerCommand>::SharedPtr rpm_pub_;
    int port_, server_fd_{-1};
    std::thread server_thread_;
    std::atomic<bool> running_;
};

int main(int argc, char* argv[]) { rclcpp::init(argc, argv); rclcpp::spin(std::make_shared<RMSServer>()); rclcpp::shutdown(); return 0; }
