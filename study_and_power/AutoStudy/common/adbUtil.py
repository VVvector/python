# -*- coding:utf-8 -*-
import re
import subprocess
from time import sleep
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)


class ADB(object):
    def __init__(self, path=Path('./temp/ui.xml'), is_virtual: bool = True, host='127.0.0.1', port=7555):
        subprocess.Popen('adb version', shell=True)
        self.path = path
        self.is_virtual = is_virtual
        self.host = host
        self.port = port
        if self.is_virtual:
            self._connect()
        else:
            logger.warning('请确保安卓手机连接手机并打开USB调试!')

        self.device = self._getDevice()
        if self.device is not None:
            logger.debug('当前设备 {}'.format(self.device))
            self.ime = self._getIME()
            self.wmsize = self._size()
            self._setIME('com.android.adbkeyboard/.AdbIME')
        else:
            logger.error('未连接设备')
            raise RuntimeError('未连接任何设备')

    def _connect(self):
        cmd = 'adb connect {}:{}'.format(self.host, self.port)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def _disconnect(self):
        logger.debug('正在断开模拟器{}:{}'.format(self.host, self.port))
        cmd = 'adb disconnect {}:{}'.format(self.host, self.port)
        if 0 == subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE):
            logger.debug('断开模拟器{}:{} 成功'.format(self.host, self.port))
        else:
            logger.error('断开模拟器{}:{} 失败'.format(self.host, self.port))

    def _size(self):
        cmd = 'adb -s {} shell wm size'.format(self.device)
        res = subprocess.check_output(cmd, shell=True)
        if isinstance(res, bytes):
            wmsize = re.findall(r'\d+', str(res, 'utf-8'))
        else:
            wmsize = re.findall(r'\d+', res)
        logger.debug('屏幕分辨率：{}'.format(wmsize))
        res = [int(x) for x in wmsize]
        return res

    def _setIME(self, ime):
        cmd = 'adb -s {} shell ime set {}'.format(self.device, ime)
        if 0 == subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE):
            logger.debug('设置输入法 {} 成功'.format(ime))
            pass
        else:
            logger.error('设置输入法 {} 失败'.format(ime))

    def _getIME(self) -> list:
        cmd = 'adb -s {} shell ime list -s'.format(self.device)
        res = subprocess.check_output(cmd, shell=True)
        if isinstance(res, bytes):
            ime = re.findall(r'\S+', str(res, 'utf-8'))
        else:
            ime = re.findall('\S+', res)
        logger.debug('系统输入法：{}'.format(ime))
        return ime[0]

    def _getDevice(self) -> str:
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

    def draw(self, orientation='down', distance=100, duration=500):
        height, width = max(self.wmsize), min(self.wmsize)
        # 中点 三分之一点 三分之二点
        x0, x1, x2 = width // 2, width // 3, width // 3 * 2
        y0, y1, y2 = height // 2, height // 3, height // 3 * 2
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

    def uiautomator(self, path=None):
        if not path:
            path = self.path

        if path.exists():
            path.unlink()
        else:
            pass

        cmd = 'adb -s {} shell uiautomator dump /sdcard/ui.xml'.format(self.device)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

        cmd = 'adb -s {} pull /sdcard/ui.xml {}'.format(self.device, path)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

        if 10240 > path.stat().st_size:
            sleep(1)

    def screenshot(self, path=None):
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
        # 接收complex参数坐标
        logger.debug('滑动 {} --{}ms-> {}'.format(begin, duration, end))
        sx, sy = int(begin.real), int(begin.imag)
        dx, dy = int(end.real), int(end.imag)
        cmd = 'adb -s {} shell input swipe {} {} {} {} {}'.format(self.device, sx, sy, dx, dy, duration)
        res = subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
        return res

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
                # raise AttributeError('{} 不是可点击的坐标'.format(x))
                return False

        logger.debug('点击 ({}, {})'.format(dx, dy))
        self.swipe(dx, dy, dx, dy, duration)
        return True

    def back(self):
        cmd = 'adb -s {} shell input keyevent 4'.format(self.device)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def input(self, msg):
        cmd = 'adb -s {} shell am broadcast -a ADB_INPUT_TEXT --es msg {}'.format(self.device, msg)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def enter_activity(self, activity):
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

    def close_app(self, packet_name):
        cmd = 'adb -s {} shell am force-stop {}'.format(self.device, packet_name)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

    def get_desktop_activity(self, path=None):
        if not path:
            path = self.path

        if path.exists():
            path.unlink()
        else:
            pass

        logger.debug("dump acttivity log")
        # cmd = 'adb -s {} shell dumpsys package > /sdcard/activity.log'.format(self.device)
        cmd = "adb -s {} logcal > /sdcard/activity.log".format(self.device)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)

        cmd = 'adb -s {} pull /sdcard/activity.log{} '.format(self.device, path)
        subprocess.check_call(cmd, shell=True, stdout=subprocess.PIPE)
        sleep(5)

    def close(self):
        self._setIME(self.ime)
        if self.is_virtual:
            self._disconnect()


if __name__ == "__main__":
    pass
