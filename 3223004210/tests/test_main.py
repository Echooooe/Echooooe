# 端到端验证 main.py：正常三参/参数不足/输入文件缺失
import sys, importlib, subprocess

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
    ans  = tmp_path / "ans.txt"
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
        capture_output=True, text=True
    )
    assert proc.returncode == 2
    assert proc.stderr.strip() != ""
