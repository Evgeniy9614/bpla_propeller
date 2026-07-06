#include <gazebo/gazebo.hh>
#include <gazebo/physics/physics.hh>
#include <gazebo/common/common.hh>
#include <ignition/math/Vector3.hh>
#include <rclcpp/rclcpp.hpp>
#include <bpla_propeller_msgs/msg/propeller_command.hpp>

namespace gazebo
{
class QuadcopterThrustPlugin : public ModelPlugin
{
private:
    physics::ModelPtr model;
    physics::JointPtr motor_joints[4];
    event::ConnectionPtr update_connection;
    
    double thrust_coefficient;
    double max_rpm;
    double motor_rpm[4];
    double last_cmd_sim_time;
    int update_count;
    
    rclcpp::Node::SharedPtr ros_node;
    rclcpp::Subscription<bpla_propeller_msgs::msg::PropellerCommand>::SharedPtr rpm_sub;

public:
    QuadcopterThrustPlugin() : ModelPlugin()
    {
        for (int i = 0; i < 4; i++)
            motor_rpm[i] = 0.0;
        last_cmd_sim_time = 0.0;
        update_count = 0;
    }

    void Load(physics::ModelPtr _model, sdf::ElementPtr _sdf) override
    {
        this->model = _model;
        
        if (!rclcpp::ok())
            rclcpp::init(0, nullptr);
        
        this->ros_node = rclcpp::Node::make_shared("quadcopter_thrust_plugin");
        
        this->thrust_coefficient = _sdf->Get<double>("thrust_coefficient", 1.0e-5).first;
        this->max_rpm = _sdf->Get<double>("max_rpm", 8000.0).first;
        
        std::string joint_names[4] = {
            "prop_1_joint", "prop_2_joint", "prop_3_joint", "prop_4_joint"
        };
        
        for (int i = 0; i < 4; i++)
        {
            this->motor_joints[i] = this->model->GetJoint(joint_names[i]);
            if (this->motor_joints[i])
                RCLCPP_INFO(this->ros_node->get_logger(), "Found joint: %s", joint_names[i].c_str());
            else
                RCLCPP_ERROR(this->ros_node->get_logger(), "Joint [%s] not found!", joint_names[i].c_str());
        }
        
        this->rpm_sub = this->ros_node->create_subscription<bpla_propeller_msgs::msg::PropellerCommand>(
            "/propeller/cmd", 10,
            [this](bpla_propeller_msgs::msg::PropellerCommand::SharedPtr msg) {
                RCLCPP_INFO(this->ros_node->get_logger(), "Got RPM: %.1f", msg->rpm);
                for (int i = 0; i < 4; i++)
                    this->motor_rpm[i] = msg->rpm;
                this->last_cmd_sim_time = this->model->GetWorld()->SimTime().Double();
            }
        );
        
        this->update_connection = event::Events::ConnectWorldUpdateBegin(
            std::bind(&QuadcopterThrustPlugin::OnUpdate, this)
        );
        
        RCLCPP_INFO(this->ros_node->get_logger(), 
            "Plugin loaded. k=%.5f, max_rpm=%.0f", thrust_coefficient, max_rpm);
    }

    void OnUpdate()
    {
        update_count++;
        double current_sim_time = this->model->GetWorld()->SimTime().Double();
        
        if ((current_sim_time - this->last_cmd_sim_time) > 0.5)
        {
            for (int i = 0; i < 4; i++)
                this->motor_rpm[i] = 0.0;
        }
        
        double total_thrust = 0.0;
        for (int i = 0; i < 4; i++)
        {
            if (!this->motor_joints[i]) continue;
                
            double rpm = std::min(this->motor_rpm[i], this->max_rpm);
            double thrust = this->thrust_coefficient * rpm * rpm;
            total_thrust += thrust;
            
            ignition::math::Vector3d force(0, 0, thrust);
            this->motor_joints[i]->GetChild()->AddRelativeForce(force);
        }
        
        // Лог каждые 100 кадров
        if (update_count % 100 == 0 && total_thrust > 0.01)
        {
            RCLCPP_INFO(this->ros_node->get_logger(), 
                "Total thrust: %.2f N, RPM: %.0f", total_thrust, motor_rpm[0]);
        }
    }
};

GZ_REGISTER_MODEL_PLUGIN(QuadcopterThrustPlugin)
}
