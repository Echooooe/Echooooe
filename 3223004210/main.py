# main.py

"""
命令行入口（带扩展功能 -n）：
- 基础功能：读取两段文本 -> 计算相似度 -> 写入 ans.txt（保留两位小数+换行）
- 扩展功能：可选参数 -n N 指定字符 n-gram 的窗口大小（默认 2）
- 退出码约定（与原先一致）：
    1：参数错误（例如缺少文件路径、-n 非正整数等）
    2：运行期异常（I/O 错误、读取失败等）
"""
import sys

from src.io_utils import read_text_file, write_text_file
from src.sim import similarity_ratio

# 统一的用法提示文本（参数错误时打印）
USAGE = "Usage: python main.py <orig_path> <copy_path> <ans_path> [-n N]"


def _parse_cli(argv):
    """
    轻量命令行解析（不引入 argparse，保持与原逻辑一致）：
    支持三种传参方式：
      1) python main.py orig.txt copy.txt ans.txt
      2) python main.py orig.txt copy.txt ans.txt -n 3
      3) python main.py -n=3 orig.txt copy.txt ans.txt
    返回: (orig_path, copy_path, ans_path, n)
    """
    n = 2  # 默认 n-gram 窗口大小（扩展功能默认值）
    files = []  # 收集位置参数（3 个文件路径）
    i = 0
    while i < len(argv):
        tok = argv[i]
        # 形式 1：-n 3
        if tok == "-n":
            # 缺少 N
            if i + 1 >= len(argv):
                print(USAGE)
                sys.exit(1)
            # N 必须是 int 且 > 0
            try:
                n = int(argv[i + 1])
            except ValueError:
                print(USAGE)
                sys.exit(1)
            i += 2
            continue
        # 形式 2：-n=3
        if tok.startswith("-n="):
            try:
                n = int(tok.split("=", 1)[1])
            except ValueError:
                print(USAGE)
                sys.exit(1)
            i += 1
            continue
        # 其他：位置参数（文件路径）
        files.append(tok)
        i += 1

    # 必须严格 3 个文件路径；n 必须为正整数
    if len(files) != 3 or n <= 0:
        print(USAGE)
        sys.exit(1)

    return files[0], files[1], files[2], n


def main():
    """
    主流程：
      1) 解析命令行参数（兼容旧用法 + 扩展 -n）
      2) 安全读取文件（UTF-8, ignore）
      3) 计算相似度（0.00~1.00）
      4) 输出到目标文件（两位小数+换行）
    异常处理：
      - 任何运行期异常 -> 打印到 stderr，退出码 2
    """
    # 解析参数（内部会在参数错误时退出码 1）
    orig_path, copy_path, ans_path, n = _parse_cli(sys.argv[1:])

    try:
        # 读取输入
        orig_text = read_text_file(orig_path)
        copy_text = read_text_file(copy_path)

        # 计算相似度（扩展：n 可调；默认 2）
        score = similarity_ratio(orig_text, copy_text, n=n)

        # 写出结果：四舍五入保留两位 + 换行
        write_text_file(ans_path, f"{score:.2f}\n")

    except (FileNotFoundError, IsADirectoryError) as e:
        # 路径不存在 / 传了目录
        sys.stderr.write(f"文件路径错误：{e}\n")
        sys.exit(2)

    except PermissionError as e:
        # 没有读/写权限
        sys.stderr.write(f"权限错误：{e}\n")
        sys.exit(2)

    except UnicodeDecodeError as e:
        # 文本编码不对（例如不是 UTF-8）
        sys.stderr.write(f"文件编码错误：{e}\n")
        sys.exit(2)

    except OSError as e:
        # 其他 I/O 异常（磁盘/句柄等）
        sys.stderr.write(f"I/O 错误：{e}\n")
        sys.exit(2)

    except ValueError as e:
        # 内容解析/参数取值问题（例如相似度函数里对非法 n 的检查）
        sys.stderr.write(f"输入内容格式错误：{e}\n")
        sys.exit(2)


# 脚本直接执行时才运行 main；被 import 时不执行
if __name__ == "__main__":
    main()
