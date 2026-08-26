#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include <gazebo/common/Plugin.hh>
#include <gazebo/physics/Joint.hh>
#include <gazebo/physics/Link.hh>
#include <gazebo/physics/Model.hh>
#include <gazebo/physics/PhysicsEngine.hh>
#include <gazebo/physics/World.hh>
#include <gazebo_ros/node.hpp>
#include <ignition/math/Pose3.hh>
#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/string.hpp>

namespace gazebo
{

/// Welds a named model to the UR gripper on "attach <model>" and releases it
/// on "detach <model>". This emulates a perfectly stiff grasp, which ODE
/// cannot sustain stably for light pinched objects.
class GraspWelder : public WorldPlugin
{
public:
  void Load(physics::WorldPtr world, sdf::ElementPtr sdf) override
  {
    world_ = world;
    ros_node_ = gazebo_ros::Node::Get(sdf);

    sub_ = ros_node_->create_subscription<std_msgs::msg::String>(
      "grasp_weld", 10,
      [this](const std_msgs::msg::String::SharedPtr msg) { OnMsg(msg); });

    RCLCPP_INFO(ros_node_->get_logger(),
                "[grasp_welder] ready on ~/%s (world '%s')",
                "grasp_weld", world->Name().c_str());
  }

private:
  // fixed-joint lumping in the URDF->SDF conversion can rename/merge links,
  // so try several known names and fall back to the first available link
  physics::LinkPtr FindLink(
    const physics::ModelPtr & model,
    const std::vector<std::string> & candidates,
    const std::string & label)
  {
    for (const auto & n : candidates) {
      auto l = model->GetLink(n);
      if (l) {
        return l;
      }
    }
    auto links = model->GetLinks();
    std::ostringstream names;
    for (const auto & l : links) {
      names << l->GetName() << " ";
    }
    RCLCPP_WARN(ros_node_->get_logger(),
      "[grasp_welder] none of {%s} on %s; links are: %s - using first",
      [&] {
        std::ostringstream c;
        for (const auto & n : candidates) {c << n << ",";}
        return c.str();
      }().c_str(), label.c_str(), names.str().c_str());
    return links.empty() ? nullptr : links[0];
  }

  void OnMsg(const std_msgs::msg::String::SharedPtr msg)
  {
    std::lock_guard<std::mutex> lock(mutex_);
    std::istringstream iss(msg->data);
    std::string cmd, model_name;
    iss >> cmd >> model_name;
    if (model_name.empty()) {
      return;
    }

    if (cmd == "attach") {
      if (joints_.count(model_name) > 0) {
        return;  // already welded
      }
      physics::ModelPtr cube = world_->ModelByName(model_name);
      physics::ModelPtr arm = world_->ModelByName("ur");
      if (!cube || !arm) {
        RCLCPP_WARN(ros_node_->get_logger(),
                    "[grasp_welder] attach: model not found (%s)", model_name.c_str());
        return;
      }
      auto gripper = FindLink(arm,
          {"gripper_base", "tool0", "flange", "wrist_3_link"}, "arm");
      auto cube_link = FindLink(cube, {"link"}, model_name);
      if (!gripper || !cube_link) {
        RCLCPP_WARN(ros_node_->get_logger(), "[grasp_welder] links not found");
        return;
      }
      physics::JointPtr joint =
        world_->Physics()->CreateJoint("fixed", arm);
      joint->SetName("grasp_weld_" + model_name);
      joint->Attach(gripper, cube_link);
      joint->Load(gripper, cube_link, ignition::math::Pose3d());
      joint->Init();
      joints_[model_name] = joint;
      RCLCPP_INFO(ros_node_->get_logger(),
                  "[grasp_welder] %s welded to %s",
                  model_name.c_str(), gripper->GetName().c_str());
    } else if (cmd == "detach") {
      auto it = joints_.find(model_name);
      if (it != joints_.end()) {
        it->second->Detach();
        joints_.erase(it);
        RCLCPP_INFO(ros_node_->get_logger(),
                    "[grasp_welder] %s released", model_name.c_str());
      }
    }
  }

  physics::WorldPtr world_;
  gazebo_ros::Node::SharedPtr ros_node_;
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr sub_;
  std::map<std::string, physics::JointPtr> joints_;
  std::mutex mutex_;
};

GZ_REGISTER_WORLD_PLUGIN(GraspWelder)

}  // namespace gazebo
