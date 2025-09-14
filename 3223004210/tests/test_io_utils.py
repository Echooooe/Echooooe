# 覆盖 src/io_utils.py：写读一致、异常、非法字节容错
import pytest
from src.io_utils import read_text_file, write_text_file

def test_IO_R003_001_write_then_read_roundtrip(tmp_path):
    # 目的：自动创建父目录并写入；能读回原文
    out = tmp_path / "out" / "note.txt"
    write_text_file(str(out), "你好，世界")
    assert out.exists()
    assert read_text_file(str(out)) == "你好，世界"

def test_IO_R003_002_read_missing_file_raises(tmp_path):
    # 目的：读取不存在文件时抛 FileNotFoundError
    missing = tmp_path / "no" / "such" / "file.txt"
    with pytest.raises(FileNotFoundError):
        read_text_file(str(missing))

def test_IO_R003_003_read_ignores_invalid_utf8(tmp_path):
    # 目的：非法 UTF-8 字节被忽略，不应抛异常
    p = tmp_path / "bad.txt"
    p.write_bytes(b"\xff\xfehello")
    assert "hello" in read_text_file(str(p))
