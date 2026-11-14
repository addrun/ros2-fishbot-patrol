# SPDX-License-Identifier: Apache-2.0
"""Optional speech service: log-only, local espeak-ng, or Edge TTS."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import rclpy
from rclpy.node import Node
from autopatrol_interfaces.srv import SpeachText

class Speaker(Node):
    def __init__(self, default_backend='log'):
        super().__init__('speaker')
        self.declare_parameter('backend', default_backend)
        self.declare_parameter('voice', 'zh-CN-XiaoxiaoNeural')
        self.declare_parameter('espeak_voice', 'cmn')
        self.service = self.create_service(SpeachText, 'speech_text', self.callback)

    @staticmethod
    def executable(name):
        path = shutil.which(name)
        if path is None:
            raise RuntimeError(f'Optional executable is missing: {name}')
        return path

    def callback(self, request, response):
        response.result = False
        text = request.text.strip()
        if not text or len(text) > 2000:
            self.get_logger().warning('Speech text must contain 1 to 2000 characters.')
            return response
        try:
            backend = self.get_parameter('backend').value
            if backend == 'log':
                self.get_logger().info(f'[speech/log] {text}')
            elif backend == 'espeak':
                subprocess.run([self.executable('espeak-ng'), '-v',
                                self.get_parameter('espeak_voice').value, text],
                               check=True, timeout=30)
            elif backend == 'edge':
                with tempfile.TemporaryDirectory(prefix='fishbot-speech-') as directory:
                    media = str(Path(directory) / 'speech.mp3')
                    subprocess.run([self.executable('edge-tts'), '--text', text,
                                    '--voice', self.get_parameter('voice').value,
                                    '--write-media', media], check=True, timeout=30)
                    subprocess.run([self.executable('mpg123'), '-q', media],
                                   check=True, timeout=30)
            else:
                raise ValueError(f'Unknown speech backend: {backend}')
            response.result = True
        except (RuntimeError, ValueError, OSError, subprocess.SubprocessError) as error:
            self.get_logger().error(f'Speech failed: {error}')
        return response

def main(args=None, default_backend='log'):
    rclpy.init(args=args)
    node = Speaker(default_backend)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
