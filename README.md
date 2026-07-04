
# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | Custom Messages | RViz**

Проект RSE БПЛА


## 📋 Что реализовано

- ✅ Кастомное сообщение `PropellerCommand` (rpm + motor_name)
- ✅ Симулятор оборотов `propeller_sim` (синусоида 1000±200 RPM)
- ✅ Визуализация в RViz `propeller_viz` (втулка + две лопасти LINE_STRIP)
- ✅ Ручное управление RPM через `ros2 topic pub`
- ✅ Авто-остановка при потере связи (таймаут 0.5 сек)


## 🏗️ Архитектура

bpla_propeller_msgs/ # Пакет сообщений
├── msg/
│ └── PropellerCommand.msg # float64 rpm, string motor_name
└── CMakeLists.txt
bpla_propeller/ # Пакет управления и визуализации
├── bpla_propeller/
│ ├── propeller_sim.py # Симулятор оборотов
│ └── propeller_viz.py # 3D-визуализация (RViz MarkerArray)
├── CMakeLists.txt
└── package.xml


## 🔧 Запуск

# Клонировать репозиторий
cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git

# Сборка
cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash

# Терминал 1: RViz
rviz2
# Fixed Frame → world, Add → By topic → /propeller/markers

# Терминал 2: Визуализация
ros2 run bpla_propeller propeller_viz.py

# Терминал 3: Управление RPM
ros2 topic pub /propeller/cmd bpla_propeller_msgs/msg/PropellerCommand "{rpm: 600.0, motor_name: 'main'}" -r 10


## 🎮 Управление

# Медленно
ros2 topic pub /propeller/cmd ... "{rpm: 200.0, ...}" -1

# Быстро (взлётный режим)
ros2 topic pub /propeller/cmd ... "{rpm: 2500.0, ...}" -1

# Остановка
ros2 topic pub /propeller/cmd ... "{rpm: 0.0, ...}" -1
