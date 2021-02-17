#!/usr/bin/env python
# -*- coding:utf-8 -*-
import re
import subprocess
from time import sleep
from pathlib import Path


class Adble(object):
    def __init__(self, path, is_virtual, host, port):
        # subprocess.Popen(f'adb version', shell=True)
        self.path = path
        self.is_virtual = is_virtual
        self.host = host
        self.port = port
        if self.is_virtual:
            self._connect()          
        else:
            print(f'请确保安卓手机连接手机并打开USB调试!')
        self.device = self._getDevice()
        if self.device is not None:
            print(f'当前设备 {self.device}')
            self.ime = self._getIME()
            self.wmsize = self._size()
            self._setIME('com.android.adbkeyboard/.AdbIME')
        else:
            print(f'未连接设备')
            raise RuntimeError(f'未连接任何设备')
        #self._startApp()

    def _startApp(self):
        print("正在打开APP……")
        res = subprocess.check_call(f'adb -s {self.device} shell input tap 157 129', shell=True, stdout=subprocess.PIPE)
        sleep(50)
    def _connect(self):
        '''连接模拟器adb connect host:port'''
        subprocess.check_call(f'adb connect {self.host}:{self.port}', shell=True, stdout=subprocess.PIPE)

        
    def _disconnect(self):
        '''连接模拟器adb connect host:port'''
        print(f'正在断开模拟器{self.host}:{self.port}')
        if 0 == subprocess.check_call(f'adb disconnect {self.host}:{self.port}', shell=True, stdout=subprocess.PIPE):
            print(f'断开模拟器{self.host}:{self.port} 成功')
        else:
            print(f'断开模拟器{self.host}:{self.port} 失败')

    def draw(self, orientation='down', distance=100, duration=500):
        height, width = max(self.wmsize), min(self.wmsize) # example: [1024, 576]
        # 中点 三分之一点 三分之二点
        x0, x1, x2 = width//2, width//3, width//3*2 
        y0, y1, y2 = height//2, height//3, height//3*2
        if 'down' == orientation:
            self.swipe(x0, y1, x0, y1+distance, duration)
        elif 'up' == orientation:
            self.swipe(x0, y2, x0, y2-distance, duration)
        elif 'left' == orientation:
            self.swipe(x2, y0, x2-distance, y0, duration)
        elif 'right' == orientation:
            self.swipe(x1, y0, x1+distance, y0, duration)
        else:
            print(f'没有这个方向 {orientation} 无法划动')
        return 0
    
    def _size(self):
        res = subprocess.check_output(f'adb -s {self.device} shell wm size', shell=True)
        if isinstance(res, bytes):
            wmsize = re.findall(r'\d+', str(res, 'utf-8'))
        else:
            wmsize = re.findall(r'\d+', res)
        #print(f'屏幕分辨率：{wmsize}')
        res = [int(x) for x in wmsize]
        return res
    

    def _setIME(self, ime):
        #print(f'设置输入法 {ime}')
        #print(f'正在设置输入法 {ime}')
        if 0 == subprocess.check_call(f'adb -s {self.device} shell ime set {ime}', shell=True, stdout=subprocess.PIPE):
            #print(f'设置输入法 {ime} 成功')
            pass
        else:
            print(f'设置输入法 {ime} 失败')

    def _getIME(self)->list:
        #print(f'获取系统输入法list')
        res = subprocess.check_output(f'adb -s {self.device} shell ime list -s', shell=True)
        if isinstance(res, bytes):
            # ime = re.findall(r'\d+', str(res, 'utf-8'))
            ime = re.findall(r'\S+', str(res, 'utf-8'))
        else:
            ime = re.findall('\S+', res)
        #print(f'系统输入法：{ime}')
        return ime[0]

    def _getDevice(self)->str:
        res = subprocess.check_output(f'adb devices', shell=True)
        if isinstance(res, bytes):
            res = str(res, 'utf-8')
        devices = re.findall(r'(.*)\tdevice', res)
        print(f'已连接设备 {devices}')
        if self.is_virtual and f'{self.host}:{self.port}' in devices:
            return f'{self.host}:{self.port}'
        elif 0 == len(devices):
            return None
        else:
            return devices[0]

    def uiautomator(self, path=None, filesize=10240):
        if not path:
            path = self.path
        for i in range(3):
            if path.exists():
                path.unlink()   #删除文件
            else:
                pass
            subprocess.check_call(f'adb -s {self.device} shell uiautomator dump /sdcard/ui.xml', shell=True, stdout=subprocess.PIPE)
            # \$MuMu共享文件夹/
            #sleep(1)
            subprocess.check_call(f'adb -s {self.device} pull /sdcard/ui.xml {path}', shell=True, stdout=subprocess.PIPE)
            if filesize < path.stat().st_size:
                break
            else:
                sleep(1)

    def screenshot(self, path=None):
        if not path:
            path = self.path
        subprocess.check_call(f'adb -s {self.device} shell screencap -p /sdcard/ui.png', shell=True, stdout=subprocess.PIPE)
        # sleep(1)
        subprocess.check_call(f'adb -s {self.device} pull /sdcard/ui.png {path}', shell=True, stdout=subprocess.PIPE)

    def swipe(self, sx, sy, dx, dy, duration):
        ''' swipe from (sx, xy) to (dx, dy) in duration ms'''
        # adb shell input swipe 500 500 500 200 500
        #print(f'滑动操作 ({sx}, {sy}) --{duration}ms-> ({dx}, {dy})')
        res = subprocess.check_call(f'adb -s {self.device} shell input swipe {sx} {sy} {dx} {dy} {duration}', shell=True, stdout=subprocess.PIPE)
        # sleep(1)
        return res

    def slide(self, begin, end, duration=500):
        '''接收complex参数坐标'''
        #print(f'滑动操作 {begin} --{duration}ms-> {end}')
        sx, sy = int(begin.real), int(begin.imag)
        dx, dy = int(end.real), int(end.imag)
        res = subprocess.check_call(f'adb -s {self.device} shell input swipe {sx} {sy} {dx} {dy} {duration}', shell=True, stdout=subprocess.PIPE)
        return res


    def tap(self, x, y=None, duration=50):
        '''改进tap为长按50ms，避免单击失灵'''
        if y is not None:
            if isinstance(x, int) and isinstance(y, int):
                dx, dy = int(x), int(y)
            else:
                print(f'输入坐标有误')
        else:
            try:
                dx, dy = int(x.real), int(x.imag)
            except Exception as e:
                #raise AttributeError(f'{x} 不是可点击的坐标')
                return False
        #print(f'触摸操作 ({dx}, {dy})')
        self.swipe(dx, dy, dx, dy, duration)
        return True

    def back(self):
        subprocess.check_call(f'adb -s {self.device} shell input keyevent 4', shell=True, stdout=subprocess.PIPE)


    def input(self, msg):
        subprocess.check_call(f'adb -s {self.device} shell am broadcast -a ADB_INPUT_TEXT --es msg {msg}', shell=True, stdout=subprocess.PIPE)
        
    def enter_activity(self, activity):
        subprocess.check_call(f'adb -s {self.device} shell am start -n {activity}', shell=True, stdout=subprocess.PIPE)
        
    def get_activity(self):
        res = subprocess.check_output(f'adb -s {self.device} shell dumpsys activity \| findstr mFocusedActivity', shell=True, stdout=subprocess.PIPE)
        if isinstance(res, bytes):
            # ime = re.findall(r'\d+', str(res, 'utf-8'))
            ime = re.findall(r' ', str(res, 'utf-8'))
        else:
            ime = re.findall(' ', res)
        #print(f'系统输入法：{ime}')
        return ime[0]
        
    def close_app(self, packet_name):
        subprocess.check_call(f'adb -s {self.device} shell am force-stop {packet_name}', shell=True, stdout=subprocess.PIPE)
        
    def close(self):
        self._setIME(self.ime)
        if self.is_virtual:
            self._disconnect()

if __name__ == "__main__":
    pass 

    
