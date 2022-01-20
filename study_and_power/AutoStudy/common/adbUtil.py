# -*- coding:utf-8 -*-
import re
import subprocess
from time import sleep
from pathlib import Path
from . import util

logger = util.get_logger(__name__)


class ADB(object):
    KEYCODE_HOME = 3  # home键
    KEYCODE_MENU = 82  # menu键
    KEYCODE_BACK = 4  # back键
    KEYCODE_POWER = 26  # power键
    KEYCODE_DPAD_UP = 19  # 向上
    KEYCODE_DPAD_DOWN = 20  # 向下
    KEYCODE_DPAD_LEFT = 21  # 向左
    KEYCODE_DPAD_RIGHT = 22  # 向右
    KEYCODE_DEL = 67  # 删除
    KEYCODE_NOTIFICATION = 83  # 解锁

    def __init__(self, path=Path('./temp/ui.xml'), is_virtual: bool = True, host='127.0.0.1', port=7555):
        subprocess.Popen('adb version', shell=True)
        self.path = path
        self.is_virtual = is_virtual
        self.host = host
        self.port = port

        if self.is_virtual:
            self.connect_device()
        else:
            logger.info('请确保安卓手机连接手机并打开USB调试!')

        self.device = self.get_device()
        if self.device is not None:
            logger.debug('当前设备 {}'.format(self.device))
            self.ime = self.get_ime()
            self.wm_size = self.screen_size()
            self.set_ime('com.android.adbkeyboard/.AdbIME')
        else:
            logger.error('未连接设备')
            raise RuntimeError('未连接任何设备')

    def close(self):
        self.set_ime(self.ime)
        if self.is_virtual:
            self.disconnect_device()

    def connect_device(self):
        cmd = 'adb connect {}:{}'.format(self.host, self.port)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def disconnect_device(self):
        logger.debug('正在断开{}:{}'.format(self.host, self.port))
        cmd = 'adb disconnect {}:{}'.format(self.host, self.port)
        if 0 == subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE):
            logger.debug('断开连接{}:{} 成功'.format(self.host, self.port))
        else:
            logger.error('断开连接{}:{} 失败'.format(self.host, self.port))

    def screen_size(self):
        cmd = 'adb -s {} shell wm size'.format(self.device)
        res = subprocess.check_output(cmd, shell=True)
        if isinstance(res, bytes):
            wm_size = re.findall(r'\d+', str(res, 'utf-8'))
        else:
            wm_size = re.findall(r'\d+', res)
        logger.debug('屏幕分辨率：{}'.format(wm_size))
        res = [int(x) for x in wm_size]
        return res

    def set_ime(self, ime):
        cmd = 'adb -s {} shell ime set {}'.format(self.device, ime)
        if 0 == subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE):
            logger.debug('设置输入法 {} 成功'.format(ime))
            pass
        else:
            logger.error('设置输入法 {} 失败'.format(ime))

    def get_ime(self) -> list:
        cmd = 'adb -s {} shell ime list -s'.format(self.device)
        res = subprocess.check_output(cmd, shell=True)
        if isinstance(res, bytes):
            ime = re.findall(r'\S+', str(res, 'utf-8'))
        else:
            ime = re.findall('\S+', res)
        logger.debug('系统输入法：{}'.format(ime))
        return ime[0]

    def get_device(self) -> str:
        cmd = 'adb devices'
        res = subprocess.check_output(cmd, shell=True)
        if isinstance(res, bytes):
            res = str(res, 'utf-8')
        devices = re.findall(r'(.*)\tdevice', res)
        logger.debug('已连接设备 {}'.format(devices))
        dev = '{}:{}'.format(self.host, self.port)
        if self.is_virtual and dev in devices:
            return dev
        elif 0 == len(devices):
            return ''
        else:
            return devices[0]

    def get_position_xml(self, path=None, file_size=10240):
        if not path:
            path = self.path

        for i in range(3):
            if path.exists():
                path.unlink()

            cmd = 'adb -s {} shell uiautomator dump /sdcard/ui.xml'.format(self.device)
            subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
            cmd = 'adb -s {} pull /sdcard/ui.xml {}'.format(self.device, path)
            subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
            if file_size < path.stat().st_size:
                break
            else:
                sleep(1)

    def get_screenshot(self, path=None):
        if not path:
            path = self.path
        cmd = 'adb -s {} shell screencap -p /sdcard/ui.png'.format(self.device)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
        cmd = 'adb -s {} pull /sdcard/ui.png {}'.format(self.device, path)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def swipe(self, sx, sy, dx, dy, duration):
        # swipe from (sx, sy) to (dx, dy) in duration ms
        logger.debug('滑动 ({}, {}) --{}ms-> ({}, {})'.format(sx, sy, duration, dx, dy))
        cmd = 'adb -s {} shell input swipe {} {} {} {} {}'.format(self.device, sx, sy, dx, dy, duration)
        res = subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
        return res

    def slide(self, begin, end, duration=500):
        logger.debug('滑动 {} --{}ms-> {}'.format(begin, duration, end))
        sx, sy = int(begin.real), int(begin.imag)
        dx, dy = int(end.real), int(end.imag)
        return self.swipe(sx, sy, dx, dy, duration)

    def draw(self, orientation='down', distance=100, duration=500):
        height, width = max(self.wm_size), min(self.wm_size)
        x0, x1, x2 = width // 2, width // 3, width // 3 * 2
        y0, y1, y2 = height // 2, height // 3, height // 5 * 3
        if 'down' == orientation:
            self.swipe(x0, y1, x0, y1 + distance, duration)
        elif 'up' == orientation:
            self.swipe(x0, y2, x0, y2 - distance, duration)
        elif 'left' == orientation:
            self.swipe(x2, y0, x2 - distance, y0, duration)
        elif 'right' == orientation:
            self.swipe(x1, y0, x1 + distance, y0, duration)
        else:
            logger.warning('没有这个方向, {} 无法划动'.format(orientation))
        return 0

    def tap(self, x, y=None, duration=50):
        if y is not None:
            if isinstance(x, int) and isinstance(y, int):
                dx, dy = int(x), int(y)
            else:
                logger.warning('输入坐标有误')
                return False
        else:
            try:
                dx, dy = int(x.real), int(x.imag)
            except Exception as e:
                logger.debug('{}是不可点击的坐标'.format(x))
                return False

        logger.debug('点击 ({}, {})'.format(dx, dy))
        self.swipe(dx, dy, dx, dy, duration)
        return True

    def input(self, msg):
        cmd = 'adb -s {} shell am broadcast -a ADB_INPUT_TEXT --es msg {}'.format(self.device, msg)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def set_activity(self, activity):
        logger.debug("activity: {}".format(activity))
        cmd = 'adb -s {} shell am start -n {}'.format(self.device, activity)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def get_activity(self):
        cmd = 'adb -s {} shell dumpsys activity \| findstr mFocusedActivity'.format(self.device)
        res = subprocess.check_output(cmd, shell=True, stdout=subprocess.PIPE)
        if isinstance(res, bytes):
            # ime = re.findall(r'\d+', str(res, 'utf-8'))
            ime = re.findall(r' ', str(res, 'utf-8'))
        else:
            ime = re.findall(' ', res)
        logger.debug('系统输入法：{}'.format(ime))
        return ime[0]

    def close_app(self, app_packet_name):
        cmd = 'adb -s {} shell am force-stop {}'.format(self.device, app_packet_name)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 点击返回键
    def back(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_BACK)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 删除
    def delete(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_DEL)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 点击home键
    def home(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_HOME)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 点击菜单键
    def menu(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_MENU)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 按一下电源键
    def power(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_POWER)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 向上滑动
    def up(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_DPAD_UP)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 向下滑动
    def down(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_DPAD_DOWN)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 向左滑动
    def left(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_DPAD_LEFT)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    # 向右滑动
    def right(self):
        cmd = 'adb shell input keyevent {}'.format(self.KEYCODE_DPAD_RIGHT)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)


if __name__ == "__main__":
    pass
