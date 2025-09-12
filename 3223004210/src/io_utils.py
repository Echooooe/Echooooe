# io_utils.py
from pathlib import Path  # Path 对象比字符串更安全、可跨平台

def read_text_file(path: str) -> str:
    """
    安全地读取文本文件（UTF-8），并忽略无法解码的非法字符。
    参数:
        path: 文件路径（字符串）
    返回:
        文件内容（字符串）
    可能抛出:
        FileNotFoundError: 当文件不存在或不是普通文件时
    """
    p = Path(path)  # 将字符串路径封装成 Path 对象，便于做存在性/类型检查
    if not p.exists() or not p.is_file():
        # 明确抛错；外层 main 会捕获并以友好方式退出
        raise FileNotFoundError(f"Input file not found: {path}")
    # 读取：UTF-8 编码；errors='ignore' 表示遇到非法字节就跳过，避免解码异常中断程序
    return p.read_text(encoding="utf-8", errors="ignore")

def write_text_file(path: str, content: str) -> None:
    """
    安全地向指定路径写入文本（UTF-8）。
    若上级目录不存在，会自动创建（parents=True）。
    参数:
        path: 输出文件路径
        content: 要写入的字符串内容
    """
    p = Path(path)
    # 确保父目录存在；parents=True 允许递归创建多级目录；exist_ok=True 表示已存在也不报错
    p.parent.mkdir(parents=True, exist_ok=True)
    # 写入文本（UTF-8 编码）
    p.write_text(content, encoding="utf-8")
