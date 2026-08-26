cmake_minimum_required(VERSION 3.8)
project(ur_lab_gazebo)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(gazebo_dev REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(gazebo REQUIRED)

add_library(grasp_welder SHARED src/grasp_welder.cpp)
ament_target_dependencies(grasp_welder rclcpp std_msgs gazebo_ros)
target_include_directories(grasp_welder PRIVATE
  ${GAZEBO_INCLUDE_DIRS}
  ${GAZEBO_DEV_INCLUDE_DIRS}
)
target_link_libraries(grasp_welder ${GAZEBO_LIBRARIES})

install(TARGETS grasp_welder LIBRARY DESTINATION lib)

# make GAZEBO_PLUGIN_PATH point at our lib dir when the ws is sourced
ament_environment_hooks("env-hooks/ur_lab_gazebo.dsv")

ament_package()
