
# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | URDF | RViz | TF2 | PID Control**
## 📦 Проекты

### 1. Propeller Simulator (`bpla_propeller_msgs` + `bpla_propeller`)
- ✅ Кастомное сообщение `PropellerCommand` (rpm + motor_name)
- ✅ Симулятор оборотов `propeller_sim` (синусоида 1000±200 RPM)
- ✅ 3D-визуализация `propeller_viz` (RViz MarkerArray LINE_STRIP)
- ✅ Ручное управление RPM через `ros2 topic pub`
- ✅ Авто-остановка при потере связи (таймаут 0.5 сек)

### 2. Quadcopter URDF Model (`bpla_description`)
- ✅ Кинематическая схема квадрокоптера типа X4
- ✅ Иерархия TF: `base_link` → `arm` → `motor` → `prop`
- ✅ Вращающиеся пропеллеры (joint type: continuous)
- ✅ Массы и моменты инерции
- ✅ Визуализация в RViz с полным TF-деревом

### 3. RPM → URDF Bridge (`propeller_joint_bridge`)
- ✅ Мост между `PropellerCommand` (RPM) и `JointState` (углы)
- ✅ Все 4 пропеллера вращаются синхронно от команд RPM
- ✅ Публикация всех 12 joint'ов для полного TF-дерева

### 4. Gazebo Simulation (`bpla_gazebo`)
- ✅ Запуск Gazebo с ROS 2
- ✅ Spawn дрона из URDF
- ✅ Сервис `/apply_link_wrench` для приложения тяги
- ⚠️ Требуется доработка графического стека в Docker

### 5. PID Hover Controller (`bpla_control`)
- ✅ PID-регулятор высоты (Kp=300, Ki=40, Kd=100)
- ✅ Математическая модель дрона (масса 2 кг, k=2e-5)
- ✅ Автоматический расчёт RPM висения (495 RPM)
- ✅ Стабилизация на 10 метрах за 2 секунды
- ✅ Анти-windup защита интегральной составляющей

## 🏗️ Архитектура


~/bpla_ws/src/
├── bpla_propeller_msgs/ # Кастомные ROS 2 сообщения
│ └── msg/
│ └── PropellerCommand.msg
├── bpla_propeller/ # Управление и визуализация пропеллера
│ ├── propeller_sim.py # Симулятор RPM
│ ├── propeller_viz.py # 3D-визуализация (MarkerArray)
│ └── propeller_joint_bridge.py # RPM → JointStates
├── bpla_description/ # URDF-модель квадрокоптера
│ ├── urdf/
│ │ └── quadcopter.urdf # Кинематическая схема
│ └── launch/
│ ├── display.launch.py
│ ├── display_bridge.launch.py
│ └── display_with_propellers.launch.py
├── bpla_gazebo/ # Симуляция в Gazebo
│ ├── scripts/
│ │ └── thrust_controller.py
│ ├── launch/
│ │ └── simulate.launch.py
│ └── worlds/
│ └── empty_with_plugins.world
└── bpla_control/ # PID-регулятор высоты
└── bpla_control/
└── hover_controller.py


## 🔧 Быстрый старт


# Клонировать репозиторий
cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git

# Сборка
cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash


# Пропеллер (Проект 1)


ros2 run bpla_propeller propeller_viz.py &
rviz2
# Add → /propeller/markers
ros2 topic pub /propeller/cmd bpla_propeller_msgs/msg/PropellerCommand "{rpm: 600.0, motor_name: 'main'}" -r 10


# URDF + мост (Проект 2-3)
ros2 launch bpla_description display_with_propellers.launch.py
# RViz: Fixed Frame → base_link, Add → RobotModel, Description Topic → /robot_description
ros2 topic pub /propeller/cmd ... "{rpm: 600.0, ...}" -r 10
# PID-регулятор (Проект 5)

ros2 run bpla_control hover_controller
# Дрон взлетает на 10 метров и стабилизируется


