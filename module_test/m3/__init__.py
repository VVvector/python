import os
import sys

cur_path = os.path.dirname(os.path.abspath(__file__))
if cur_path not in sys.path:
    sys.path.append(cur_path)
