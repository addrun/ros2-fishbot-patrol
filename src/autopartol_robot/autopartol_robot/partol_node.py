# SPDX-License-Identifier: Apache-2.0
"""Nav2 waypoint patrol with a background sensor executor."""
from pathlib import Path
import threading
import time

import cv2
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
import rclpy
from rclpy.duration import Duration
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from tf2_ros import Buffer, TransformException, TransformListener
from tf_transformations import quaternion_from_euler
from autopatrol_interfaces.srv import SpeachText
from autopartol_robot.patrol_utils import image_path, parse_waypoints

class PatrolNode(Node):
    def __init__(self):
        super().__init__('patrol_node')
        self.declare_parameter('initial_point', [0.0, 0.0, 0.0])
        self.declare_parameter('target_points', [1.0, 0.0, 0.0])
        self.declare_parameter('image_save_path', str(Path.home() / '.ros/fishbot_patrol/pictures'))
        self.declare_parameter('loop', True)
        self.declare_parameter('max_cycles', 0)
        self.declare_parameter('navigation_timeout', 120.0)
        self.declare_parameter('image_wait_timeout', 5.0)
        self.initial = parse_waypoints(self.get_parameter('initial_point').value)
        if len(self.initial) != 1:
            raise ValueError('initial_point must contain exactly one [x, y, yaw] triple.')
        self.points = parse_waypoints(self.get_parameter('target_points').value)
        if self.get_parameter('navigation_timeout').value <= 0:
            raise ValueError('navigation_timeout must be positive.')
        if self.get_parameter('image_wait_timeout').value <= 0:
            raise ValueError('image_wait_timeout must be positive.')
        if self.get_parameter('max_cycles').value < 0:
            raise ValueError('max_cycles must be nonnegative.')
        self.output_dir = Path(self.get_parameter('image_save_path').value).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.speech_client = self.create_client(SpeachText, 'speech_text')
        self.bridge = CvBridge()
        self.latest_image = None
        self.image_time = 0.0
        self.image_lock = threading.Lock()
        self.subscription_image = self.create_subscription(
            Image, '/camera/image_raw', self.image_callback, qos_profile_sensor_data)

    def image_callback(self, message):
        with self.image_lock:
            self.latest_image = message
            self.image_time = time.monotonic()

    def record_image(self):
        deadline = time.monotonic() + self.get_parameter('image_wait_timeout').value
        while rclpy.ok() and time.monotonic() < deadline:
            with self.image_lock:
                image = self.latest_image
                fresh = time.monotonic() - self.image_time < 2.0
            if image is not None and fresh:
                break
            time.sleep(0.05)
        else:
            self.get_logger().error('No fresh camera image; capture skipped.')
            return False
        try:
            transform = self.buffer.lookup_transform(
                'map', 'base_footprint', rclpy.time.Time(), Duration(seconds=1.0)).transform
            if image.encoding == '32FC1':
                pixels = self.bridge.imgmsg_to_cv2(image, desired_encoding='passthrough')
                pixels = cv2.convertScaleAbs(pixels, alpha=255.0 / 5.0)
            else:
                pixels = self.bridge.imgmsg_to_cv2(image, desired_encoding='bgr8')
            path = image_path(self.output_dir, time.time_ns(),
                              transform.translation.x, transform.translation.y)
            if not cv2.imwrite(str(path), pixels):
                raise OSError(f'OpenCV could not write {path}')
            self.get_logger().info(f'Image saved: {path}')
            return True
        except (TransformException, OSError, cv2.error, ValueError) as error:
            self.get_logger().error(f'Image capture failed: {error}')
            return False

    def speak(self, text):
        self.get_logger().info(text)
        if self.speech_client.service_is_ready():
            request = SpeachText.Request()
            request.text = text
            self.speech_client.call_async(request)

def pose_at(navigator, point):
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x, pose.pose.position.y = point[:2]
    quaternion = quaternion_from_euler(0.0, 0.0, point[2])
    (pose.pose.orientation.x, pose.pose.orientation.y,
     pose.pose.orientation.z, pose.pose.orientation.w) = quaternion
    return pose

def main(args=None):
    rclpy.init(args=args)
    patrol = None
    navigator = None
    executor = None
    worker = None
    failures = 0
    try:
        patrol = PatrolNode()
        navigator = BasicNavigator(node_name='patrol_navigator')
        navigator.set_parameters([Parameter(
            'use_sim_time', value=patrol.get_parameter('use_sim_time').value)])
        executor = MultiThreadedExecutor(num_threads=2)
        executor.add_node(patrol)
        worker = threading.Thread(target=executor.spin, daemon=True)
        worker.start()
        navigator.setInitialPose(pose_at(navigator, patrol.initial[0]))
        navigator.waitUntilNav2Active()
        cycle = 0
        while rclpy.ok():
            for index, point in enumerate(patrol.points, 1):
                if not rclpy.ok():
                    break
                patrol.speak(f'前往航点 {index}: x={point[0]:.2f}, y={point[1]:.2f}')
                if not navigator.goToPose(pose_at(navigator, point)):
                    failures += 1
                    patrol.get_logger().error('Navigation goal was rejected.')
                    continue
                started = time.monotonic()
                timed_out = False
                while rclpy.ok() and not navigator.isTaskComplete():
                    if time.monotonic() - started > patrol.get_parameter('navigation_timeout').value:
                        navigator.cancelTask()
                        patrol.get_logger().error('Navigation timed out; goal canceled.')
                        timed_out = True
                        break
                    time.sleep(0.05)
                if not timed_out and navigator.getResult() == TaskResult.SUCCEEDED:
                    if patrol.record_image():
                        patrol.speak('已到达航点，图像记录完成')
                    else:
                        failures += 1
                else:
                    failures += 1
                    patrol.get_logger().warning('Waypoint not reached; no success image recorded.')
            cycle += 1
            patrol.get_logger().info(f'Patrol cycle {cycle} completed; failures={failures}')
            limit = patrol.get_parameter('max_cycles').value
            if not patrol.get_parameter('loop').value or (limit and cycle >= limit):
                break
    except KeyboardInterrupt:
        pass
    except Exception as error:
        failures += 1
        if patrol is not None:
            patrol.get_logger().error(str(error))
        else:
            print(f'Patrol initialization failed: {error}')
    finally:
        if (navigator is not None and rclpy.ok() and navigator.result_future is not None
                    and not navigator.result_future.done()):
            navigator.cancelTask()
        if executor is not None:
            executor.shutdown(timeout_sec=2.0)
        if worker is not None:
            worker.join(timeout=2.0)
        # BasicNavigator spins synchronous futures on the global executor.
        # Stop it before destroying its action clients.
        rclpy.get_global_executor().shutdown(timeout_sec=2.0)
        if navigator is not None:
            navigator.destroy_node()
        if patrol is not None:
            patrol.destroy_node()
        rclpy.try_shutdown()
    return 1 if failures else 0

if __name__ == '__main__':
    raise SystemExit(main())
