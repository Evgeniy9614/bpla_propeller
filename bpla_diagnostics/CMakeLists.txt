cmake_minimum_required(VERSION 3.8)
project(bpla_diagnostics)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(bpla_propeller_msgs REQUIRED)

add_executable(vibration_monitor src/vibration_monitor.cpp)
target_include_directories(vibration_monitor PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
ament_target_dependencies(vibration_monitor
  rclcpp sensor_msgs std_msgs bpla_propeller_msgs)

add_executable(imu_simulator src/imu_simulator.cpp)
target_include_directories(imu_simulator PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
ament_target_dependencies(imu_simulator
  rclcpp sensor_msgs bpla_propeller_msgs)

install(TARGETS
  vibration_monitor
  imu_simulator
  DESTINATION lib/${PROJECT_NAME})

ament_package()
