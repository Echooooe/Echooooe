# src/__init__.py
from . import io_utils, sim, text_norm

from .io_utils import read_text_file, write_text_file
from .sim import similarity_ratio

__all__ = [
    "io_utils", "sim", "text_norm",
    "read_text_file", "write_text_file", "similarity_ratio",
]
