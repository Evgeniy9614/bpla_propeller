# 🚁 BPLA Propeller Simulator & Visualization

**ROS 2 Humble | Python | URDF | RViz | TF2 | PID | State Machine | Computer Vision**

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
- ✅ Авто-остановка при потере связи

### 4. Gazebo Simulation (`bpla_gazebo`)

- ✅ Запуск Gazebo с ROS 2
- ✅ Spawn дрона из URDF
- ✅ Сервис `/apply_link_wrench` для приложения тяги
- ✅ C++ плагин тяги (базовый)

### 5. PID Hover Controller (`bpla_control`)

- ✅ PID-регулятор высоты (Kp=300, Ki=40, Kd=100)
- ✅ Математическая модель дрона (масса 2 кг, k=2e-5)
- ✅ Стабилизация на 10 метрах за 2 секунды
- ✅ Анти-windup защита интегральной составляющей

### 6. Mission Controller (`bpla_control`)

- ✅ Конечный автомат (State Machine) на 5 состояний
- ✅ Автоматический цикл миссии: GROUND → TAKEOFF → HOVER → WAYPOINT → LAND
- ✅ Полёт по 4 точкам (квадрат 5×5 м), циклическое повторение

### 7. Vision Landing Controller (`bpla_control`)

- ✅ Посадка на AprilTag по визуальной метке
- ✅ Симуляция камеры с перспективной проекцией и шумом
- ✅ Конечный автомат: SEARCH → APPROACH → LAND → DONE
- ✅ Точность посадки < 1 см

### 8. FFT Vibration Monitor (`bpla_diagnostics`) — C++

- ✅ Быстрое преобразование Фурье (FFT) на 1024 точках
- ✅ Имитатор акселерометра (1000 Гц) с моделированием вибраций
- ✅ Удаление DC-компоненты (гравитации)
- ✅ Поиск пиков на гармониках RPM (1×, 2×, 3×)
- ✅ Предупреждения при превышении порога вибрации
- ✅ Настраиваемый порог через ROS 2 параметры

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
            ┌──────────────────────┼──────────────────────────┐
            │                      │                          │
            ▼                      ▼                          ▼
    ┌───────────────┐    ┌─────────────────┐    ┌──────────────────────┐
    │ propeller_viz │    │ propeller_joint │    │ bpla_control         │
    │   (Python)    │    │    _bridge      │    │   (Python)           │
    │               │    │   (Python)      │    │                      │
    │ MarkerArray   │    │                 │    │ hover_controller     │
    │ втулка +      │    │ RPM → угол      │    │ mission_controller   │
    │ 2 лопасти     │    │ 12 joint'ов     │    │ landing_controller   │
    └───────┬───────┘    └───────┬─────────┘    └──────────┬───────────┘
            │                    │                         │
            ▼                    ▼                         │
          RViz            /joint_states                    │
                      ┌───────────────┐                    │
                      │ robot_state_  │                    │
                      │   publisher   │                    │
                      └───────┬───────┘                    │
                              │                            │
                              ▼                            │
                        /tf (TF-дерево)                    │
                              │                            │
                              ▼                            │
                            RViz                           │
                      (RobotModel)                         │
                                                           │
                                             ┌─────────────┴─────────────┐
                                             │   Математическая модель   │
                                             │   T = k × RPM²            │
                                             │   a = (4T - mg) / m       │
                                             │   v = v + a·dt            │
                                             │   h = h + v·dt            │
                                             └───────────────────────────┘
        

## 🔄 Поток данных

```
МИССИЯ
  │  Определяет цель высоты, состояние
  ▼
PID-регулятор
  │  RPM = hover_rpm + Kp·err + Ki·∫err + Kd·derr/dt
  ▼
/propeller/cmd
  │
  ├──► propeller_viz ──► MarkerArray ──► RViz (3D пропеллер)
  │
  ├──► propeller_joint_bridge ──► /joint_states
  │                                    │
  │                                    ▼
  │                            robot_state_publisher
  │                                    │
  │                                    ▼
  │                              /tf ──► RViz (модель дрона)
  │
  ├──► imu_simulator (C++) ──► /imu/data_raw
  │                                    │
  │                                    ▼
  │                            vibration_monitor (C++)
  │                                    │
  │                              FFT: сигнал → спектр
  │                                    │
  │                              ⚠️ WARNING (амплитуда > порог)
  │
  └──► (модель физики) ──► высота/скорость ──► снова PID ↩︎
```

## 🤖 Конечные автоматы (State Machine)

### Миссия (mission_controller)

```

     ┌──────────┐
     │  GROUND  │◄───────────────────────────────────┐
     └────┬─────┘                                    │
          │ через 2 сек                              │
          ▼                                          │
     ┌──────────┐                                    │
     │ TAKEOFF  │  (взлёт на 10 м)                   │
     └────┬─────┘                                    │
          │ H ≈ цель, V ≈ 0                          │
          ▼                                          │
     ┌──────────┐                                    │
     │  HOVER   │  (стабилизация 3 сек)              │
     └────┬─────┘                                    │
          │ через 3 сек                              │
          ▼                                          │
     ┌──────────┐     все 4 точки                    │
     │ WAYPOINT │─── пройдены ──────────┐            │
     └──────────┘                       │            │
                                        ▼            │
                                   ┌──────────┐      │
                                   │   LAND   │      │
                                   └────┬─────┘      │
                              (посадка) │ H < 0.1 м  │ 
                                        └────────────┘
   
|  Состояние   |        Что делает        |    Условие перехода  |
|--------------|--------------------------|----------------------|
| **GROUND**   | Стоим на земле, ждём     |   Через 2 секунды    |
| **TAKEOFF**  | Взлетаем на 10 м         |   Достигли высоты    |
| **HOVER**    | Висим, стабилизируемся   |   Через 3 секунды    |
| **WAYPOINT** | Летим по точкам (5×5 м)  | Все 4 точки пройдены |
| **LAND**     | Садимся | Высота < 0.1 м |
```

### Посадка на метку (landing_controller)

```
     ┌──────────┐
     │  SEARCH  │  (поиск метки, 3 сек)
     └────┬─────┘
          │ метка найдена
          ▼
     ┌──────────┐
     │ APPROACH │  (снижение + движение к метке)
     └────┬─────┘
          │ над меткой, H < 5 м
          ▼
     ┌──────────┐
     │   LAND   │  (вертикальная посадка)
     └────┬─────┘
          │ H < 0.1 м
          ▼
     ┌──────────┐
     │   DONE   │  (миссия завершена)
     └──────────┘
     
|  Состояние   |        Что делает        |    Условие перехода  |
|--------------|--------------------------|----------------------|
| **SEARCH**   | Висим на 10 м, ищем метку| Через 3 секунды      |
| **APPROACH** | Снижаемся, летим к метке | Над меткой и H < 5 м |
| **LAND**     | Вертикальная посадка     | Высота < 0.1 м       |
| **DONE**     |    Миссия завершена      |         —            |
```

## 🌳 Кинематическая схема (TF)

```
    world (неподвижная земля)
      │
      └── base_link (корпус, серый куб 20×20×5 см)
            │
            ├── arm_1_joint (fixed, 45°) ── arm_1 (чёрный цилиндр)
            │     └── motor_1_joint (fixed) ── motor_1 (оранжевый)
            │           └── prop_1_joint (continuous, ось Z) ── prop_1 (белый)
            │
            ├── arm_2_joint (fixed, 135°) ── arm_2
            │     └── motor_2_joint (fixed) ── motor_2
            │           └── prop_2_joint (continuous) ── prop_2
            │
            ├── arm_3_joint (fixed, 225°) ── arm_3
            │     └── motor_3_joint (fixed) ── motor_3
            │           └── prop_3_joint (continuous) ── prop_3
            │
            └── arm_4_joint (fixed, 315°) ── arm_4
                  └── motor_4_joint (fixed) ── motor_4
                        └── prop_4_joint (continuous) ── prop_4

    Типы сочленений:
    fixed — жёсткое (сварка, болты)
    continuous — бесконечное вращение (подшипник)
```

## 📦 Зависимости пакетов

```
  bpla_propeller_msgs           ← сообщения (не зависит ни от кого)
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
    bpla_propeller               bpla_control
    (визуализация, мост)         (PID, миссия, посадка)
         │                              │
         │                              │
         ▼                              │
    bpla_description                    │
    (URDF, launch)                      │
         │                              │
         │                              │
         ▼                              ▼
    bpla_gazebo                  bpla_diagnostics
    (симуляция)                    (FFT, C++)
```

## 🏗️ Структура репозитория

```
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
```

## 🔧 Быстрый старт

### Клонировать репозиторий

cd ~/bpla_ws/src
git clone https://github.com/Evgeniy9614/bpla_propeller.git

### Сборка

cd ~/bpla_ws
colcon build --symlink-install
source install/setup.bash

| Проект           | Команда                                                                                   |
| ---------------- | ----------------------------------------------------------------------------------------- |
| Пропеллер + RViz | `ros2 run bpla_propeller propeller_viz.py`                                                |
| URDF + мост      | `ros2 launch bpla_description display_with_propellers.launch.py`                          |
| PID-регулятор    | `ros2 run bpla_control hover_controller`                                                  |
| Миссия           | `ros2 run bpla_control mission_controller`                                                |
| Посадка на метку | `ros2 run bpla_control landing_controller`                                                |
| FFT + IMU        | `ros2 run bpla_diagnostics imu_simulator` + `ros2 run bpla_diagnostics vibration_monitor` |
| Управление RPM   | `ros2 topic pub /propeller/cmd ... "{rpm: 600.0}" -r 10`                                  |


