#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, TwistStamped

class VelHelper(Node):
    def __init__(self):
        super().__init__('vel_helper')
        
        # 1. 订阅 /cmd_vel (来自键盘或 Nav2)
        self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10)
        
        # 2. 发布 /fishbot_diff_drive_controller/cmd_vel (给控制器)
        self.pub = self.create_publisher(
            TwistStamped,
            '/fishbot_diff_drive_controller/cmd_vel',
            10)
            
        self.get_logger().info('转换节点已启动: /cmd_vel -> TwistStamped')

    def cmd_vel_callback(self, msg):
        # 创建带时间戳的消息
        stamped_msg = TwistStamped()
        stamped_msg.header.stamp = self.get_clock().now().to_msg()
        stamped_msg.header.frame_id = 'base_footprint' # 坐标系通常设为基座
        stamped_msg.twist = msg
        
        # 转发出去
        self.pub.publish(stamped_msg)

def main(args=None):
    rclpy.init(args=args)
    node = VelHelper()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()

if __name__ == '__main__':
    main()