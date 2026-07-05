
# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | URDF | RViz | TF2**

## 📦 Проекты

### 1. Propeller Simulator (`bpla_propeller_msgs` + `bpla_propeller`)
- Кастомное сообщение `PropellerCommand` (rpm + motor_name)
- Симулятор оборотов (синусоида 1000±200 RPM)
- Визуализация пропеллера в RViz (MarkerArray LINE_STRIP)
- Ручное управление RPM через `ros2 topic pub`
- Авто-остановка при потере связи (таймаут 0.5 сек)

### 2. Quadcopter URDF Model (`bpla_description`)
- Кинематическая схема квадрокоптера типа X4
- Иерархия: `base_link` → `arm` → `motor` → `prop`
- Вращающиеся пропеллеры (joint type: continuous)
- Массы и моменты инерции
- Визуализация в RViz с TF-фреймами
- Интерактивное управление через Joint State Publisher GUI

---

## 🏗️ Архитектура



## 🏗️ Архитектура

bpla_ws/src/
├── bpla_propeller_msgs/ # Кастомные ROS 2 сообщения
│ └── msg/
│ └── PropellerCommand.msg
├── bpla_propeller/ # Управление и визуализация пропеллера
│ ├── propeller_sim.py # Симулятор RPM
│ └── propeller_viz.py # 3D-визуализация (MarkerArray)
└── bpla_description/ # URDF-модель квадрокоптера
├── urdf/
│ └── quadcopter.urdf # Кинематическая схема
└── launch/
└── display.launch.py # Запуск RViz + TF


## 🔧 Запуск

# Клонировать репозиторий
cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git

# Сборка
cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash

# Пропеллер (Проект 1)

# Терминал 1: Симулятор
ros2 run bpla_propeller propeller_sim.py

# Терминал 2: Управление RPM
ros2 topic pub /propeller/cmd bpla_propeller_msgs/msg/PropellerCommand "{rpm: 600.0, motor_name: 'main'}" -r 10
#URDF-модель (Проект 3)

ros2 launch bpla_description display.launch.py
# В RViz: Fixed Frame → base_link, Add → RobotModel
# Окно Joint State Publisher GUI → крутить пропеллеры слайдерами


