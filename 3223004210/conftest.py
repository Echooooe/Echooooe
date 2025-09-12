# 3223004210/conftest.py
import sys
from pathlib import Path

# 把 3223004210 目录本身加到 sys.path，确保可以 import src
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
