# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | C++ | URDF | RViz | TF2 | PID | FFT | CV | MAVLink | RMS**

## **ROS 2 Humble | Python | C++ | URDF | RViz | TF2 | PID | FFT | Computer Vision | MAVLink | RMS**

A comprehensive educational UAV simulation platform built on **ROS 2 Humble**, demonstrating the complete software stack of a quadcopter—from propeller simulation and visualization to autonomous flight control, diagnostics, MAVLink communication, and remote management.
The project showcases practical implementations of:

- ROS 2 nodes and custom interfaces
- URDF robot modeling
- TF2 frame hierarchy
- Gazebo simulation
- PID flight control
- Computer vision–based autonomous landing
- FFT vibration analysis
- MAVLink communication
- Remote drone management over TCP

---

# 📦 Projects

## 1. Propeller Simulator (`bpla_propeller_msgs` + `bpla_propeller`)

A ROS 2 package for simulating quadcopter propeller RPM and visualizing rotor motion in RViz.

### Features

- ✅ Custom `PropellerCommand` message (`rpm` + `motor_name`)
- ✅ Propeller RPM simulator (`propeller_sim`) generating a **1000 ± 200 RPM** sinusoidal signal
- ✅ 3D propeller visualization using **RViz MarkerArray (LINE_STRIP)**
- ✅ Manual RPM control via `ros2 topic pub`
- ✅ Automatic motor shutdown after communication timeout (0.5 s)

---

## 2. Quadcopter URDF Model (`bpla_description`)

A complete URDF description of an X4 quadcopter.

### Features

- ✅ X-configuration quadcopter model
- ✅ TF hierarchy:
  `base_link → arm → motor → propeller`
- ✅ Continuously rotating propellers
- ✅ Physical mass and inertia parameters
- ✅ Full TF visualization in RViz

---

## 3. RPM → URDF Bridge (`propeller_joint_bridge`)

A bridge converting propeller RPM commands into URDF joint rotations.

### Features

- ✅ Converts `PropellerCommand` messages into `JointState`
- ✅ Synchronizes all four propellers with incoming RPM commands
- ✅ Publishes all 12 joints for a complete TF tree
- ✅ Automatic stop on communication timeout

---

## 4. Gazebo Simulation (`bpla_gazebo`)

A physics-based simulation environment for the quadcopter.

### Features

- ✅ Gazebo integration with ROS 2
- ✅ Drone spawning directly from the URDF model
- ✅ `/apply_link_wrench` service for external force application
- ✅ Basic C++ thrust controller plugin

---

## 5. PID Hover Controller (`bpla_control`)

A closed-loop altitude controller based on a PID algorithm.

### Features

- ✅ PID altitude controller (`Kp=300`, `Ki=40`, `Kd=100`)
- ✅ Mathematical quadcopter model
  - Mass: **2 kg**
  - Thrust coefficient: **2×10⁻⁵**
- ✅ Stable hover at **10 m** within approximately **2 seconds**
- ✅ Integral anti-windup protection

---

## 6. Mission Controller (`bpla_control`)

An autonomous mission controller implemented as a finite-state machine.

### Features

- ✅ Five-state autonomous mission logic
- ✅ Mission sequence:
  
  ```
  GROUND
  ↓
  TAKEOFF
  ↓
  HOVER
  ↓
  WAYPOINT
  ↓
  LAND
  ```
- ✅ Automatic flight through four waypoints (5 × 5 m square)
- ✅ Continuous mission loop

---

## 7. Vision Landing Controller (`bpla_control`)

Autonomous landing using AprilTag visual guidance.

### Features

- ✅ Precision landing using AprilTag detection
- ✅ Camera simulator with perspective projection and image noise
- ✅ Landing state machine:
  
  ```
  SEARCH
  ↓
  APPROACH
  ↓
  LAND
  ↓
  DONE
  ```
- ✅ Landing accuracy better than **1 cm**

---

## 8. FFT Vibration Monitor (`bpla_diagnostics`)

Real-time vibration analysis implemented in **C++**.

### Features

- ✅ 1024-point Fast Fourier Transform (FFT)
- ✅ IMU simulator running at **1000 Hz**
- ✅ DC offset (gravity) removal
- ✅ Harmonic peak detection (1×, 2×, 3× RPM)
- ✅ Configurable vibration threshold
- ✅ Automatic vibration warnings

---

## 9. MAVLink Integration (`bpla_mavlink`)

A communication bridge between ROS 2 and MAVLink-compatible flight controllers such as **Pixhawk** and **PX4**.

### Features

- ✅ ROS 2 ↔ MAVLink bridge
- ✅ Simulated HEARTBEAT, telemetry, and control commands
- ✅ Supported MAVLink messages:
  - HEARTBEAT (0)
  - ATTITUDE (30)
  - GLOBAL_POSITION_INT (33)
- ✅ Supported commands:
  - TAKEOFF
  - LAND
  - GOTO
  - RETURN TO LAUNCH (RTL)
- ✅ Published ROS 2 topics:
  - `/mavlink/position`
  - `/mavlink/setpoint`
  - `/mavlink/battery`

---

## 10. RMS — Remote Management System (`bpla_remote`)

A client-server application for remote drone control.

### Features

- ✅ Multithreaded TCP server (C++)
- ✅ Python operator console
- ✅ Remote command execution:
  - TAKEOFF
  - LAND
  - RPM
  - STATUS
- ✅ ROS 2 integration
- ✅ TCP-based remote management architecture

## 🏗️ Архитектура системы

                             ┌─────────────────────────┐
                             │   ros2 topic pub        │
                             │   /propeller/cmd        │
                             │   "{rpm: 600}"          │
                             └────────────┬────────────┘
                                          │
                                          ▼
                        ┌─────────────────────────────────┐
                        │       /propeller/cmd            │
                        │    (PropellerCommand)           │
                        │    float64 rpm                  │
                        │    string motor_name            │
                        └──────────┬──────────────────────┘
                                   │
            ┌──────────────────────┼──────────────────────────┐───────────────────┐
            │                      │                          │                   │    
            ▼                      ▼                          ▼                   ▼
    ┌───────────────┐    ┌─────────────────┐    ┌──────────────────────┐   ┌──────────────┐
    │ propeller_viz │    │ propeller_joint │    │ bpla_control         │   │ bpla_mavlink │
    │   (Python)    │    │    _bridge      │    │   (Python)           │   │ (C++/Python) │
    │               │    │   (Python)      │    │                      │   │              │
    │ MarkerArray   │    │                 │    │ hover_controller     │   │  HEARTBEAT   │
    │ RViz          │    │ RPM → JointState│    │ mission_controller   │   │  SETPOINT    │
    │               │    │                 │    │ landing_controller   │   │  TELEMETRY   │
    └───────┬───────┘    └───────┬─────────┘    └──────────┬───────────┘   └──────┬───────┘
            │                    │                         │                      │                      
            ▼                    ▼                         │                      ▼
          RViz            /joint_states                    │                /mavlink/position
                      ┌───────────────┐                    │                /mavlink/setpoint
                      │ robot_state_  │                    │                /mavlink/battery
                      │   publisher   │                    │
                      └───────┬───────┘                    │
                              │                            │
                              ▼                            │
                        /tf (TF-Tree)                      │
                              │                            │
                              ▼                            │
                            RViz                           │
                         (RobotModel)                      │
                                                           │
                                             ┌─────────────┴─────────────┐
                                             │   Mathematical Model      │
                                             │   T = k × RPM²            │
                                             │   a = (4T - mg) / m       │
                                             │   v = v + a·dt            │
                                             │   h = h + v·dt            │
                                             └───────────────────────────┘
     The architecture follows a modular ROS 2 design, where each subsystem is implemented as an 
     independent package communicating through ROS topics, services, and TF transforms. 
     This modular approach makes the project easy to extend with additional sensors, controllers, 
     or autonomous behaviors.                                        

The architecture follows a modular ROS 2 design, where each subsystem is implemented as an independent package communicating through ROS topics, services, and TF transforms. This modular approach makes the project easy to extend with additional sensors, controllers, or autonomous behaviors.      

### 🔄 Data Flow

The control pipeline starts with the mission controller, which generates altitude or position setpoints. These references are processed by the PID controller, which computes the required propeller RPM values.
The generated RPM commands are distributed to multiple ROS 2 nodes responsible for visualization, robot state updates, diagnostics, communication, and the mathematical flight model.

```

Mission Controller
  │  Defines flight state and altitude target
  ▼
PID Controller
  │  RPM = hover_rpm + Kp·error + Ki·∫error + Kd·d(error)/dt
  ▼
/propeller/cmd
  │
  ├──► propeller_viz ──► MarkerArray ──► RViz 
  │
  │
  ├──► propeller_joint_bridge ──► /joint_states
  │                                    │
  │                                    ▼
  │                            robot_state_publisher
  │                                    │
  │                                    ▼
  │                                   TF2 ──► RViz
  │ 
  │
  ├──► mavlink_bridge ──► /mavlink/position 
  │                   ──► /mavlink/setpoint 
  │                   ──► /mavlink/battery 
  │
  │
  ├──► imu_simulator (C++) ──► /imu/data_raw
  │                                    │
  │                                    ▼
  │                            vibration_monitor
  │                                    │
  │                              FFT Spectrum Analysis
  │                                    │
  │                               Vibration Warning
  │
  │
  └──► Flight Dynamics Model ──►  Altitude / Velocity ──► PID Feedback ↩︎
```

## 🤖 Finite-State Machines

### The project includes two autonomous finite-state machines:

- Mission Controller
- Vision Landing Controller

## Mission Controller

The mission controller executes a complete autonomous flight cycle.

```
     ┌──────────┐
     │  GROUND  │◄───────────────────────────────────┐
     └────┬─────┘                                    │
          │ after 2 s                                │
          ▼                                          │
     ┌──────────┐                                    │
     │ TAKEOFF  │                                    │
     └────┬─────┘                                    │
          │ target altitude reached                  │
          ▼                                          │
     ┌──────────┐                                    │
     │  HOVER   │                                    │
     └────┬─────┘                                    │
          │ after 3 s                                │
          ▼                                          │
     ┌──────────┐ all waypoints completed            │
     │ WAYPOINT │───────────────────────┐            │
     └──────────┘                       │            │
                                        ▼            │
                                   ┌──────────┐      │
                                   │   LAND   │      │
                                   └────┬─────┘      │
                       altitude < 0.1 m │            │ 
                                        └────────────┘
```

### Mission States

| State        | Description                  | Transition Condition    |
| ------------ | ---------------------------- | ----------------------- |
| **GROUND**   | Waiting on the ground        | After 2 seconds         |
| **TAKEOFF**  | Ascend to 10 m               | Target altitude reached |
| **HOVER**    | Stabilize at target altitude | After 3 seconds         |
| **WAYPOINT** | Fly through four waypoints   | All waypoints completed |
| **LAND**     | Controlled descent           | Altitude < 0.1 m        |

##### Vision Landing Controller

The landing controller performs autonomous precision landing using AprilTag detection.

```
     ┌──────────┐
     │  SEARCH  │  
     └────┬─────┘
          │ Tag detected
          ▼
     ┌──────────┐
     │ APPROACH │  
     └────┬─────┘
          │ Above target
          ▼
     ┌──────────┐
     │   LAND   │  
     └────┬─────┘
          │ Altitude < 0.1 m
          ▼
     ┌──────────┐
     │   DONE   │  
     └──────────┘
```

### Landing States

| State        | Description                            | Transition Condition         |
| ------------ | -------------------------------------- | ---------------------------- |
| **SEARCH**   | Search for the AprilTag while hovering | Tag detected                 |
| **APPROACH** | Descend while aligning with the target | Above tag and altitude < 5 m |
| **LAND**     | Vertical landing                       | Altitude < 0.1 m             |
| **DONE**     | Mission completed                      | —                            |

##### 🔌 MAVLink Integration

The project includes a MAVLink communication bridge that enables interaction with standard Ground Control Stations (GCS) such as **QGroundControl** and flight controllers including **Pixhawk** and **PX4**.

```
 Ground Control Station
 (QGroundControl)
          │
          │ HEARTBEAT (1 Hz)
          │◄──────────────────────────────┐
          │                               │
          │ ATTITUDE (10 Hz)              │
          │◄──────────────────────────────┤
          │                               │
          │ SET_POSITION                  │
          ├──────────────────────────────►│
          │                               │
          │ COMMAND_LONG                  │
          ├──────────────────────────────►│
          │                               │
          ▼                               ▼
   Flight Controller             ROS 2 MAVLink Bridge
    (PX4 / Pixhawk)                (bpla_mavlink)
```

### Supported MAVLink Messages

| Message             | ID  | Purpose              | ROS 2 Topic         |
| ------------------- | ---:| -------------------- | ------------------- |
| HEARTBEAT           | 0   | Vehicle heartbeat    | `/mavlink/position` |
| ATTITUDE            | 30  | Roll, pitch, yaw     | `/mavlink/position` |
| GLOBAL_POSITION_INT | 33  | GPS position         | `/mavlink/position` |
| SET_POSITION_TARGET | 84  | Position command     | `/mavlink/setpoint` |
| COMMAND_LONG        | 76  | TAKEOFF / LAND / RTL | `/mavlink/setpoint` |
| BATTERY_STATUS      | 147 | Battery telemetry    | `/mavlink/battery`  |

##### Supported Commands

- TAKEOFF
- LAND
- GOTO
- RETURN TO LAUNCH (RTL)
  The MAVLink bridge enables seamless communication between ROS 2 applications and external flight controllers, making the project compatible with standard UAV software ecosystems.

## 🌳 TF Tree (Robot Kinematics)

The quadcopter model is represented as a hierarchical TF2 tree, where each component is connected through URDF joints.

```
world
│
└── base_link (Drone body)
    │
    ├── arm_1_joint (fixed, 45°)
    │      └── arm_1
    │             └── motor_1_joint (fixed)
    │                    └── motor_1
    │                           └── prop_1_joint (continuous)
    │                                  └── prop_1
    │
    ├── arm_2_joint (fixed, 135°)
    │      └── arm_2
    │             └── motor_2
    │                    └── prop_2
    │
    ├── arm_3_joint (fixed, 225°)
    │      └── arm_3
    │             └── motor_3
    │                    └── prop_3
    │
    └── arm_4_joint (fixed, 315°)
           └── arm_4
                  └── motor_4
                         └── prop_4
```

### Joint Types

| Joint Type     | Description                                    |
| -------------- | ---------------------------------------------- |
| **fixed**      | Rigid connection between components            |
| **continuous** | Unlimited rotational joint used for propellers |

##The complete TF tree is published through **robot_state_publisher** and visualized in **RViz**, enabling real-time inspection of the quadcopter's kinematic structure.

### 📦 Package Dependency Graph

The workspace is organized into independent ROS 2 packages, each responsible for a specific subsystem.

```
                  bpla_propeller_msgs
                     (ROS Interfaces)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   bpla_propeller    bpla_control    bpla_mavlink
   Visualization      Flight Logic    MAVLink Bridge
          │                │                │
          ▼                │                │
   bpla_description         │                │
      URDF Model            │                │
          │                ▼                ▼
          │        bpla_diagnostics   bpla_remote
          │        FFT Monitoring     Remote Control
          │
          ▼
     bpla_gazebo
   Physics Simulation
```

##### Package Overview

| Package                 | Description                            |
| ----------------------- | -------------------------------------- |
| **bpla_propeller_msgs** | Custom ROS 2 interfaces                |
| **bpla_propeller**      | Propeller simulation and visualization |
| **bpla_description**    | URDF quadcopter model                  |
| **bpla_gazebo**         | Gazebo simulation                      |
| **bpla_control**        | PID controller and autonomous missions |
| **bpla_diagnostics**    | FFT vibration monitoring               |
| **bpla_mavlink**        | MAVLink communication bridge           |
| **bpla_remote**         | Remote Management System (RMS)         |

All packages communicate using standard ROS 2 topics, services, and TF transforms.

## 🏗 Repository Structure

```
bpla_ws/
└── src/
    ├── bpla_propeller_msgs/
    │   └── msg/
    │       └── PropellerCommand.msg
    │
    ├── bpla_propeller/
    │   ├── propeller_sim.py
    │   ├── propeller_viz.py
    │   └── propeller_joint_bridge.py
    │
    ├── bpla_description/
    │   ├── urdf/
    │   └── launch/
    │
    ├── bpla_gazebo/
    │   ├── launch/
    │   └── scripts/
    │
    ├── bpla_control/
    │   ├── hover_controller.py
    │   ├── mission_controller.py
    │   └── landing_controller.py
    │
    ├── bpla_diagnostics/
    │   ├── src/
    │   │   ├── vibration_monitor.cpp
    │   │   └── imu_simulator.cpp
    │   └── CMakeLists.txt
    │
    ├── bpla_mavlink/
    │   ├── src/
    │   ├── bpla_mavlink/
    │   └── CMakeLists.txt
    │
    └── bpla_remote/
        ├── src/
        ├── scripts/
        └── CMakeLists.txt
```

```
The repository follows the standard **ROS 2 workspace** layout, making it straightforward to build, maintain, and extend.

---



# 🚀 Quick Start

## Clone the Repository

```bash
cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git
```

---

## Build the Workspace

```bash
cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash
```

---

## Launch Examples

| Component               | Command                                                                             |
| ----------------------- | ----------------------------------------------------------------------------------- |
| Propeller Visualization | `ros2 run bpla_propeller propeller_viz.py`                                          |
| URDF + TF Visualization | `ros2 launch bpla_description display_with_propellers.launch.py`                    |
| PID Hover Controller    | `ros2 run bpla_control hover_controller`                                            |
| Mission Controller      | `ros2 run bpla_control mission_controller`                                          |
| Vision Landing          | `ros2 run bpla_control landing_controller`                                          |
| IMU Simulator           | `ros2 run bpla_diagnostics imu_simulator`                                           |
| FFT Monitor             | `ros2 run bpla_diagnostics vibration_monitor`                                       |
| MAVLink Bridge          | `ros2 run bpla_mavlink mavlink_bridge.py`                                           |
| MAVLink Commander       | `ros2 run bpla_mavlink mavlink_commander`                                           |
| RPM Publisher           | `ros2 topic pub /propeller/cmd ... "{rpm: 600.0}" -r 10`                            |
| RMS Server              | `~/bpla_ws/install/bpla_remote/lib/bpla_remote/rms_server --ros-args -p port:=8080` |
| RMS Client              | `~/bpla_ws/install/bpla_remote/lib/bpla_remote/rms_client.py`                       |

---

# 📚 Technologies

- ROS 2 Humble
- Python
- Modern C++
- Gazebo
- RViz
- URDF
- TF2
- PID Control
- MAVLink
- AprilTag
- OpenCV
- FFT
- TCP Networking
- Git

---

# 🎯 Learning Objectives

This repository demonstrates practical implementations of:

- ROS 2 package development
- Custom ROS interfaces
- Robot modeling using URDF
- TF2 transform trees
- Autonomous flight control
- PID controller design
- UAV mission planning
- Computer vision–based landing
- FFT signal processing
- MAVLink communication
- Distributed ROS 2 architecture
- Remote drone management

---

# 📄 License

This project is intended for educational and research purposes.
Feel free to fork, modify, and extend it for your own robotics and UAV projects.
