# main.py
import sys
from io_utils import read_text_file, write_text_file
from sim import similarity_ratio

def main():
    """
    程序入口。
    命令行参数：
      argv[1] = 原文文件绝对路径
      argv[2] = 抄袭版文件绝对路径
      argv[3] = 答案输出文件绝对路径
    输出：
      在 argv[3] 指定路径写入形如 "0.78\n" 的两位小数字符串
    退出码：
      - 正常：0
      - 参数错误：1
      - 运行期异常（I/O等）：2
    """
    # 参数个数必须是 4（脚本名 + 3 个参数）
    if len(sys.argv) != 4:
        # 打印简明用法提示到 stdout（或 stderr 均可）；课程评测只看输出文件，不看这里
        print("Usage: python main.py <orig_path> <copy_path> <ans_path>")
        sys.exit(1)

    # 拿到三个路径
    orig_path, copy_path, ans_path = sys.argv[1], sys.argv[2], sys.argv[3]

    try:
        # 读取两个输入文件（UTF-8，非法字符忽略）
        orig_text = read_text_file(orig_path)
        copy_text = read_text_file(copy_path)

        # 计算相似度（默认 2-gram 余弦，相同极短文本退化为 Jaccard）
        score = similarity_ratio(orig_text, copy_text)  # 返回 0.0 ~ 1.0 的浮点数

        # 题目要求：答案文件写入“浮点型，精确到小数点后两位”
        # f"{score:.2f}\n" 会四舍五入保留两位，并加换行（有些评测会严格比较换行）
        write_text_file(ans_path, f"{score:.2f}\n")

    except Exception as e:
        # 任何异常都输出简短错误信息到 stderr，并用非零码退出
        # 这样既不会“异常退出”扣分，也方便你排查问题
        sys.stderr.write(str(e) + "\n")
        sys.exit(2)

# 仅当直接执行 main.py 时运行 main()；被当作模块导入时不会触发
if __name__ == "__main__":
    main()
