# 🚁 BPLA Propeller Simulator

**ROS 2 Humble | Python | Custom Messages**

Проект №1 

## 📋 Описание

Симулятор управления оборотами несущего винта с публикацией кастомного сообщения `PropellerCommand` в топик `/propeller/cmd`. RPM меняется по синусоидальному закону (1000 ± 200 об/мин), имитируя работу реальной системы управления двигателем.

## 🏗️ Архитектура

bpla_propeller_msgs/ # Пакет сообщений
├── msg/
│ └── PropellerCommand.msg # float64 rpm, string motor_name
└── CMakeLists.txt
bpla_propeller/ # Пакет ноды
├── bpla_propeller/
│ └── propeller_sim.py # Нода-симулятор
└── CMakeLists.txt

## 🔧 Запуск

```bash
# Клонировать репозиторий
cd ~/bpla_ws/src
git clone https://github.com/Evgenii14/bpla_propeller.git

# Сборка
cd ~/bpla_ws
colcon build --packages-select bpla_propeller_msgs bpla_propeller --symlink-install

# Запуск
source install/setup.bash
ros2 run bpla_propeller propeller_sim.py

# Проверка (в другом терминале)
ros2 topic echo /propeller/cmd

## 📦 Зависимости
    • ROS 2 Humble
    • Python 3.10+
    • rclp 
##🎯 Применение в БПЛА
    • Винты/роторы: задание оборотов через PropellerCommand.rpm
    • Тяга: RPM → тяга через аэродинамический коэффициент (в следующих проектах)
    • Микшер: распределение RPM по 4+ моторам квадрокоптера
