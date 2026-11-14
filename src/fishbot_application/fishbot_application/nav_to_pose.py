import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from rclpy.duration import Duration

def main():
    rclpy.init()
    
    # 1. 初始化 Navigator
    navigator = BasicNavigator()
    
    # 2. 等待 Nav2 激活 (如果这一步卡住，说明没有完成 Initial Pose)
    # 必须先运行 init_robot_pose 脚本，或者在 RViz 里点 2D Pose Estimate
    print("等待 Nav2 激活...")
    navigator.waitUntilNav2Active()
    print("Nav2 已激活，开始导航！")

    # 3. 设置目标点 (Frame ID 必须是 map)
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'map'
    # 使用 navigator 的时钟获取时间，确保与仿真时间同步
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    
    # 设置你的目标坐标 (请确认这个点在地图的可通行区域内)
    goal_pose.pose.position.x = 1.0
    goal_pose.pose.position.y = 1.0
    goal_pose.pose.orientation.w = 1.0 # 简单的朝向
    
    # 4. 发送指令
    navigator.goToPose(goal_pose)
    
    # 5. 循环监听反馈
    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        
        # 【关键修改】增加非空判断，防止报错
        if feedback and i % 5 == 0: # 每5次循环打印一次，防止刷屏
            print(f'预计剩余时间: {Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9:.2f} s')
            
            # 超时判断
            if Duration.from_msg(feedback.navigation_time) > Duration(seconds=600.0):
                navigator.cancelTask()
                
    # 6. 结果判断
    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('导航结果：成功到达目标点！')
    elif result == TaskResult.CANCELED:
        print('导航结果：任务被取消')
    elif result == TaskResult.FAILED:
        print('导航结果：失败')
    else:
        print('导航结果：返回状态无效')

    rclpy.shutdown()

if __name__ == '__main__':
    main()