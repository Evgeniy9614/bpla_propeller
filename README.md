
# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | URDF | RViz | TF2 | Joint States**


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
- ✅ Авто-остановка при потере связи
- ✅ Публикация всех 12 joint'ов для полного TF-дерева
## 🏗️ Архитектура


~/bpla_ws/src/
├── bpla_propeller_msgs/ # Кастомные ROS 2 сообщения
│ └── msg/
│ └── PropellerCommand.msg
├── bpla_propeller/ # Управление и визуализация
│ ├── propeller_sim.py # Симулятор RPM
│ ├── propeller_viz.py # 3D-визуализация (MarkerArray)
│ └── propeller_joint_bridge.py # RPM → JointStates
└── bpla_description/ # URDF-модель квадрокоптера
├── urdf/
│ └── quadcopter.urdf # Кинематическая схема
└── launch/
├── display.launch.py # Только модель + слайдеры
├── display_bridge.launch.py # URDF + RViz (без joint_state_publisher)
└── display_with_propellers.launch.py # Полный запуск с мостом


## 🔧 Быстрый старт


# Клонировать репозиторий
cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git

# Сборка
cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash


# Полный запуск (URDF + мост + RViz)


ros2 launch bpla_description display_with_propellers.launch.py
В RViz: Fixed Frame → base_link, Add → RobotModel
Description Topic → /robot_description

# Управление RPM (другой терминал)
ros2 topic pub /propeller/cmd bpla_propeller_msgs/msg/PropellerCommand "{rpm: 600.0, motor_name: 'main'}" -r 10



