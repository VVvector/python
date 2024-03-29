# -*- coding:utf-8 -*-
import time


class Timer:
    def __init__(self, func=time.perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError(f'Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError(f'Not Started')
        end = self._func()
        self.elapsed += end - self._start
        print("花费了 {} 秒".format(self.elapsed))
        self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
