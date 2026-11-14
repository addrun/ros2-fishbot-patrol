# SPDX-License-Identifier: Apache-2.0
import subprocess
import pytest
import rclpy
from autopatrol_interfaces.srv import SpeachText
from autopartol_robot.speaker import Speaker

@pytest.fixture
def speaker():
    rclpy.init(args=['--ros-args', '-r', '__ns:=/release_unit_tests'])
    node = Speaker()
    yield node
    node.destroy_node()
    rclpy.try_shutdown()

def request(text):
    value = SpeachText.Request()
    value.text = text
    return value

def test_log_backend_succeeds_without_audio(speaker):
    assert speaker.callback(request('offline sample'), SpeachText.Response()).result

def test_empty_text_fails(speaker):
    assert not speaker.callback(request('   '), SpeachText.Response()).result

def test_invalid_backend_fails(speaker):
    from rclpy.parameter import Parameter
    speaker.set_parameters([Parameter('backend', value='not-a-backend')])
    assert not speaker.callback(request('sample'), SpeachText.Response()).result

def test_speech_is_passed_as_single_argument(speaker, monkeypatch):
    from rclpy.parameter import Parameter
    speaker.set_parameters([Parameter('backend', value='espeak')])
    monkeypatch.setattr(Speaker, 'executable', staticmethod(lambda name: '/mock/' + name))
    calls = []
    monkeypatch.setattr(subprocess, 'run', lambda args, **kwargs: calls.append((args, kwargs)))
    text = 'quotes " and ; shell metacharacters'
    assert speaker.callback(request(text), SpeachText.Response()).result
    assert calls[0][0][-1] == text
    assert not calls[0][1].get('shell', False)

def test_failed_tts_never_plays_stale_audio(speaker, monkeypatch):
    from rclpy.parameter import Parameter
    speaker.set_parameters([Parameter('backend', value='edge')])
    monkeypatch.setattr(Speaker, 'executable', staticmethod(lambda name: '/mock/' + name))
    calls = []
    def fail(args, **kwargs):
        calls.append(args)
        raise subprocess.CalledProcessError(1, args)
    monkeypatch.setattr(subprocess, 'run', fail)
    assert not speaker.callback(request('sample'), SpeachText.Response()).result
    assert len(calls) == 1
    assert calls[0][0].endswith('edge-tts')
