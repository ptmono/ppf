import os
import sys

lib_path = os.path.abspath(__file__)
lib_path = lib_path[:os.path.dirname(lib_path).rfind('/')]
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)
