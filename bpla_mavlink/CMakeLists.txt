cmake_minimum_required(VERSION 3.8)
project(bpla_mavlink)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(bpla_propeller_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)

# C++ MAVLink Commander
add_executable(mavlink_commander src/mavlink_commander.cpp)
target_include_directories(mavlink_commander PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
ament_target_dependencies(mavlink_commander
  rclcpp bpla_propeller_msgs geometry_msgs)

# Python MAVLink Bridge
install(PROGRAMS
  bpla_mavlink/mavlink_bridge.py
  DESTINATION lib/${PROJECT_NAME})

install(TARGETS mavlink_commander
  DESTINATION lib/${PROJECT_NAME})

ament_package()
