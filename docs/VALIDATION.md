# 发布前验证记录

验证日期：2026-11-14。环境：Ubuntu 24.04.2、ROS 2 Jazzy。
本次通过的是仿真与软件验证，不是实体机器人测试或安全认证。

## 软件版本

| 组件 | 本机版本 |
| --- | --- |
| rclpy | 7.1.4 |
| ros_gz_sim | 1.0.16 |
| gz_ros2_control | 1.2.16 |
| nav2_bringup | 1.3.10 |
| controller_manager | 4.39.2 |

## 已执行并通过

| 检查 | 结果 |
| --- | --- |
| 从本仓库源码构建 | 5 个包通过，构建/安装目录与原始学习工程隔离 |
| rosdep 依赖核对 | 已满足声明的系统依赖 |
| colcon 回归测试 | 17 项，0 错误、0 失败、0 跳过 |
| 仓库资产与源码检查 | 6 项通过 |
| Xacro 展开 | 生成 FishBot URDF：11 个 link、10 个 joint |
| 场景可移植性 | 不含嵌入的重复 FishBot，不引用个人绝对路径或外部货架网格 |
| 激光雷达 | 收到 `/scan`，360 束，frame 为 `laser_link` |
| RGB 相机 | 收到 `/camera/image_raw`，640×480、rgb8，frame 为 `camera_link` |
| 里程计 | 收到 `/odom`，导航过程中位置发生变化 |
| 单航点导航与拍照 | 从初始位姿向 `(1.0, 0.0, 0.0)` 导航，Nav2 返回成功，保存 1 张 PNG，巡检进程退出码为 0 |
| 图像内容 | 人工检查保存图像，包含仿真室内场景，并非空图 |
| 语音回归 | 日志后端、空文本、无效后端、子进程参数列表和失败时不播放旧音频均经过测试；未调用在线服务 |
| 发布文件检查 | 未发现常见凭据模式；不包含教材 PDF、历史缓存或原始学习目录的运行数据 |

回归测试覆盖航点参数校验、无尾部斜杠的图像输出路径、重复航点不覆盖文件、语音错误处理及应用入口导入。
原始学习工程经过文件内容比对，没有被本次整理覆盖。

## 如何复验

```bash
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
source install/setup.bash
colcon test --event-handlers console_cohesion+
colcon test-result --verbose
python3 -m pytest -q tests
ros2 launch autopartol_robot bringup.launch.py gui:=false rviz:=false headless:=true \
  config_file:=$(ros2 pkg prefix --share autopartol_robot)/config/patrol_once.yaml
```

Nav2 成功后会在日志中输出 `Image saved` 和 `Patrol cycle 1 completed; failures=0`。
单次巡检节点退出不会自动关闭整套仿真；用 `Ctrl+C` 关闭剩余组件。

## 局限与未验证项

- 尚未遍历原始配置的所有航点，也未进行多小时、多轮连续运行测试。
- 没有验证实体机器人、真实相机/雷达、音频硬件或在线 Edge TTS 的端到端运行。
- 图形界面交互没有作为本次自动化测试范围；测试使用无 Gazebo/RViz 窗口的服务器模式。
- 本机首次将 `LIBGL_ALWAYS_SOFTWARE=1` 与 EGL headless 渲染一起使用时，Mesa/EGL 出现崩溃；移除这个强制软件渲染变量后，传感器、导航和拍照通过。不同显卡/驱动的 headless 支持仍需各自检查。
- GitHub CI 只定义构建和回归流程；本地通过不等于已观察到云端 CI 通过。
