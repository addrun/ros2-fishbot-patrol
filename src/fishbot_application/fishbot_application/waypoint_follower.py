import sys
import rclpy
from rclpy.duration import Duration
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

def main():
    # 1. 自动注入仿真时间参数，免去终端输入
    argv = sys.argv + ['--ros-args', '-p', 'use_sim_time:=true']
    rclpy.init(args=argv)
    
    navigator = BasicNavigator()
    
    # 等待导航启动
    print("等待 Nav2 激活...")
    navigator.waitUntilNav2Active()
    print("Nav2 已激活，准备发送多点巡航任务。")

    # 创建点集 (Waypoints)
    goal_poses = []
    
    # 辅助函数：快速创建 Pose
    def create_pose(x, y, w=1.0):
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = navigator.get_clock().now().to_msg()
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        pose.pose.orientation.w = w
        return pose

    # 定义路点 (根据你的地图坐标修改)
    # 注意：如果起点是(0,0)，第一个点设为(0,0)可能会瞬间完成
    goal_poses.append(create_pose(2.0, 0.0)) # 点1
    goal_poses.append(create_pose(2.0, 2.0)) # 点2
    goal_poses.append(create_pose(0.0, 0.0)) # 点3 (回到原点)

    # 调用路点导航服务
    # 注意: followWaypoints 会在每个点停顿一下，如果想不停车连续过点，需用 goThroughPoses
    print(f"发送 {len(goal_poses)} 个路点...")
    navigator.followWaypoints(goal_poses)

    # 判断结束及获取反馈
    i = 0
    while not navigator.isTaskComplete():
        i += 1
        feedback = navigator.getFeedback()
        
        # 增加非空判断，并降低打印频率
        if feedback and i % 10 == 0:
            print(f'正在前往第 {feedback.current_waypoint + 1} 个路点...')
            
    # 最终结果判断
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('导航结果：巡航完成！')
    elif result == TaskResult.CANCELED:
        print('导航结果：被取消')
    elif result == TaskResult.FAILED:
        print('导航结果：失败')
    else:
        print('导航结果：返回状态无效')

    rclpy.shutdown()

if __name__ == '__main__':
    main()