# ROS 2 FishBot 导航与巡检

基于 **ROS 2 Jazzy + Gazebo Sim + Nav2** 的移动机器人仿真项目。
将机器人模型、室内场景、已有地图、导航示例、航点巡检、到点图像记录和可选语音服务放在一个可构建的工作空间中。


## 功能包

| 包名 | 内容 |
| --- | --- |
| `fishbot_description` | Xacro 模型、差速控制器、激光/IMU/RGB-D 传感器、Gazebo 场景与话题桥接 |
| `fishbot_navigation2` | 地图、Nav2 参数、导航与可选 RViz 启动入口 |
| `fishbot_application` | 初始位姿、TF 查询、单目标和航点导航的小示例 |
| `autopatrol_interfaces` | `SpeachText.srv` 文本播报服务，沿用原接口拼写 |
| `autopartol_robot` | 巡检、到点保存图像、语音服务和组合启动，沿用原包名拼写 |

## 环境与构建

目标环境为 Ubuntu 24.04、ROS 2 Jazzy、Gazebo Sim（`ros_gz_sim` / `gz_ros2_control`）。
先安装 ROS 2 Jazzy 和 rosdep / colcon；若 rosdep 尚未初始化，仅需执行一次 `sudo rosdep init`。

```bash
git clone https://github.com/addrun/ros2-fishbot-patrol.git
cd ros2-fishbot-patrol
source /opt/ros/jazzy/setup.bash
rosdep update
rosdep install --from-paths src --ignore-src --rosdistro jazzy -r -y
colcon build --symlink-install
source install/setup.bash
```

每个新终端都要 source ROS 2 和当前工作空间。不要再叠加另一个带同名 `fishbot_description` 包的旧工作空间。

## 快速启动

一次启动仿真、导航与循环巡检：

```bash
ros2 launch autopartol_robot bringup.launch.py
```

默认显示 Gazebo 和 RViz；默认语音后端为 `log`，只记录文本，不访问网络、不开启音频播放。
Nav2 激活并完成初始定位后，机器人会按参数文件中的航点巡检。

首次使用建议先进行单航点巡检：

```bash
ros2 launch autopartol_robot bringup.launch.py       config_file:=$(ros2 pkg prefix --share autopartol_robot)/config/patrol_once.yaml
```

无桌面环境的测试入口（GPU/驱动或软件渲染环境仍需支持 EGL）：

```bash
ros2 launch autopartol_robot bringup.launch.py gui:=false rviz:=false headless:=true
```

仅启动仿真与导航，手动在 RViz 设置位姿和目标：

```bash
ros2 launch autopartol_robot bringup.launch.py patrol:=false
```

也可以分终端启动：

```bash
ros2 launch fishbot_description gazebo_sim.launch.py
ros2 launch fishbot_navigation2 navigation2.launch.py
ros2 launch autopartol_robot autopatrol.launch.py
```

## 参数与输出

默认巡检参数：`src/autopartol_robot/config/patrol_config.yaml`；单次示例：`patrol_once.yaml`。
使用自己的参数文件时传入 `config_file:=/absolute/path/to/patrol.yaml`。

| 参数 | 默认/含义 |
| --- | --- |
| `initial_point` | `[0.0, 0.0, 0.0]`，地图坐标中的 x、y、yaw（米、弧度） |
| `target_points` | 展平的 `[x, y, yaw, ...]` 数组，必须为有限数值的完整三元组 |
| `loop` | `true`：重复巡检；`false`：完成一轮后退出 |
| `max_cycles` | `0`：不限轮数；正整数：最多巡检多少轮 |
| `navigation_timeout` | 单个目标墙钟超时，默认 120 秒 |
| `image_wait_timeout` | 等待新鲜图像的墙钟超时，默认 5 秒 |
| `image_save_path` | 默认 `~/.ros/fishbot_patrol/pictures`，自动创建，无需尾部斜杠 |

图像名包含时间戳与地图位姿，重复访问同一航点不会覆盖旧图。
导航失败、超时或图像保存失败不会被报告为“拍照成功”。
`Ctrl+C` 会尝试取消当前导航并清理节点。传感器订阅使用后台执行器，避免同步导航等待阻塞图像接收。

## 可选语音

- `speech_backend:=log`：默认、无网络依赖，仅日志。
- `speech_backend:=espeak`：本地 `espeak-ng`，需要安装该工具及可用音频设备。
- `speech_backend:=edge`：在线 `edge-tts` 生成语音，`mpg123` 播放，需要网络、对应工具和音频设备。

`edge-tts` 可通过隔离的 Python 工具环境安装，例如 `pipx install edge-tts`。
确保这些可执行文件位于 `PATH`。文本通过参数列表交给子进程，不拼接 shell 命令；失败时服务返回 `false`。

## 仿真资源说明

- 场景与地图均随包安装，无需本机 Gazebo Fuel 缓存路径。
- 去掉了保存场景中嵌入的机器人，启动时只生成一台 FishBot。
- 货架外观改为其原有碰撞盒的可视化表示，不包含外部 GLB；障碍物碰撞几何和位姿保留。
- 图像桥接 `/camera/image` → `/camera/image_raw`；控制桥接 `/cmd_vel` → `/fishbot_diff_drive_controller/cmd_vel`。

## 测试与局限

```bash
colcon test --event-handlers console_cohesion+
colcon test-result --verbose
python3 -m pytest -q tests
```

测试范围和实际运行记录见 [docs/VALIDATION.md](docs/VALIDATION.md)。
CI 检查构建、Python 回归和资产完整性。
此项目不包含在线建图流程；提供的是已有地图上的定位导航与巡检。

## 许可

Apache-2.0，保留各包已有许可证。构建产物、历史备份和个人运行数据不在仓库中。
