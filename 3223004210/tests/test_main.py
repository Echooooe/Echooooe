# 端到端验证 main.py：正常三参/参数不足/输入文件缺失
import importlib
import subprocess
import sys


def _run_main_with_args(args):
    # 在同一进程内模拟命令行调用 main.main()
    if "main" in sys.modules:
        del sys.modules["main"]
    main = importlib.import_module("main")
    orig = sys.argv[:]
    try:
        sys.argv = ["main.py"] + args
        main.main()
    finally:
        sys.argv = orig


def test_MAIN_R004_001_outputs_two_decimal_similarity(tmp_path):
    # 目的：三参数端到端 -> 输出 0~1 两位小数 + 换行
    orig = tmp_path / "orig.txt"
    copy = tmp_path / "copy.txt"
    ans = tmp_path / "ans.txt"
    orig.write_text("人工智能的重要分支是机器学习。", encoding="utf-8")
    copy.write_text("机器学习是人工智能的重要分支。", encoding="utf-8")
    _run_main_with_args([str(orig), str(copy), str(ans)])
    text = ans.read_text(encoding="utf-8")
    assert text.endswith("\n")
    val = float(text.strip())
    assert 0.0 <= val <= 1.0
    assert len(text.strip().split(".")[1]) == 2  # 恰两位小数


def test_MAIN_R004_002_invalid_args_exit_code():
    # 目的：参数不足 -> Usage 提示 + 退出码 1
    proc = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
    assert proc.returncode == 1
    assert "Usage:" in (proc.stdout + proc.stderr)


def test_MAIN_R004_003_missing_input_files_returncode_2():
    # 目的：输入文件不存在 -> 退出码 2 + stderr 有错误信息
    proc = subprocess.run(
        [sys.executable, "main.py", "no_a.txt", "no_b.txt", "ans.txt"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert proc.stderr.strip() != ""


def test_MAIN_R004_004_cli_option_n_valid(tmp_path):
    """
    [扩展功能] 验证 -n 参数的正确用法：
    - 场景：提供 -n 3，程序应正常运行并生成结果文件
    - 断言：退出码为 0，输出文件存在且内容是浮点数两位小数（简单检查）
    """
    import subprocess
    import sys

    o = tmp_path / "o.txt"
    c = tmp_path / "c.txt"
    a = tmp_path / "a.txt"
    o.write_text("人工智能的重要分支是机器学习。", encoding="utf-8")
    c.write_text("机器学习是人工智能的重要分支。", encoding="utf-8")

    # -n 3 的调用
    proc = subprocess.run(
        [sys.executable, "main.py", str(o), str(c), str(a), "-n", "3"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert a.exists()
    # 简单校验“X.XX”两位小数
    out = a.read_text(encoding="utf-8").strip()
    float(out)  # 能被解析为浮点
    assert len(out.split(".")[1]) == 2  # 恰两位小数


def test_MAIN_R004_005_cli_option_n_invalid(tmp_path):
    """
    [扩展功能] 校验 -n 的非法值处理：
    - 场景：-n 0（非正整数）
    - 期望：解析阶段判定为参数错误，打印 Usage，退出码=1
    """
    import subprocess
    import sys

    o = tmp_path / "o.txt"
    c = tmp_path / "c.txt"
    a = tmp_path / "a.txt"
    o.write_text("A", encoding="utf-8")
    c.write_text("B", encoding="utf-8")

    proc = subprocess.run(
        [sys.executable, "main.py", str(o), str(c), str(a), "-n", "0"],
        capture_output=True,
        text=True,
    )
    # 参数错误：返回码 1，输出中包含 Usage
    assert proc.returncode == 1
    assert "Usage:" in (proc.stdout + proc.stderr)


def test_MAIN_R004_006_write_path_is_directory(tmp_path):
    """
    输出路径指向目录：write_text_file 内部调用 Path.write_text 抛 IsADirectoryError，
    main 捕获后应返回码 2，并在 stderr 打印错误信息。
    """
    import subprocess
    import sys

    o = tmp_path / "o.txt"
    c = tmp_path / "c.txt"
    out_dir = tmp_path / "ans_dir"
    o.write_text("A", encoding="utf-8")
    c.write_text("B", encoding="utf-8")
    out_dir.mkdir()  # 故意把“输出文件”设为一个目录
    proc = subprocess.run(
        [sys.executable, "main.py", str(o), str(c), str(out_dir)], capture_output=True, text=True
    )
    assert proc.returncode == 2
    assert proc.stderr.strip() != ""  # 有错误信息


def test_MAIN_R004_007_cli_option_n_not_int(tmp_path):
    """
    -n 非整数：参数解析阶段判定为参数错误，打印 Usage，退出码 1。
    """
    import subprocess
    import sys

    o = tmp_path / "o.txt"
    c = tmp_path / "c.txt"
    a = tmp_path / "a.txt"
    o.write_text("A", encoding="utf-8")
    c.write_text("B", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "main.py", str(o), str(c), str(a), "-n", "abc"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "Usage:" in (proc.stdout + proc.stderr)
