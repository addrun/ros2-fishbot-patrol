import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer
from tf_transformations import euler_from_quaternion
from rclpy.duration import Duration # 【修正1】引入 Duration 类

class TFListener(Node):

    def __init__(self):
        super().__init__('tf2_listener')
        # 创建缓存区，用于存储一段时间内的坐标变换数据
        self.buffer = Buffer()
        # 创建监听器，监听到的数据会自动存入 buffer
        self.listener = TransformListener(self.buffer, self)
        # 创建定时器，1Hz (每秒打印一次)
        self.timer = self.create_timer(1.0, self.get_transform)

    def get_transform(self):
        try:
            # lookup_transform(target_frame, source_frame, time, timeout)
            # time=Time() 表示获取“最新”的可用变换
            # timeout=Duration(seconds=1) 表示如果当前没数据，最多等待1秒
            tf = self.buffer.lookup_transform(
                'map', 
                'base_footprint', 
                rclpy.time.Time(), # 【修正2】直接实例化 Time() 代表最近时刻 (Time(seconds=0)也可以)
                Duration(seconds=1) # 【修正3】使用 Duration 对象
            )
            
            transform = tf.transform
            # 四元数转欧拉角 (注意顺序通常是 x, y, z, w)
            rotation_euler = euler_from_quaternion([
                transform.rotation.x,
                transform.rotation.y,
                transform.rotation.z,
                transform.rotation.w
            ])
            
            # 格式化打印，保留两位小数方便查看
            self.get_logger().info(
                f'\n平移: x={transform.translation.x:.2f}, y={transform.translation.y:.2f}, z={transform.translation.z:.2f}\n'
                f'旋转(欧拉角): roll={rotation_euler[0]:.2f}, pitch={rotation_euler[1]:.2f}, yaw={rotation_euler[2]:.2f}'
            )
            
        except Exception as e:
            # 刚启动时可能因为 TF 树还没建立好而报错，这是正常的，打印出来即可
            self.get_logger().warn(f'无法获取坐标变换: {str(e)}')


def main():
    rclpy.init()
    node = TFListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()