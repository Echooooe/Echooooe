import tkinter as tk
from tkinter import messagebox, filedialog
from Myapp import generate_exercises, grade
import os

def generate():
    try:
        n = int(entry_n.get())
        r = int(entry_r.get())
        exercises, answers = generate_exercises(n, r)
        with open("Exercises.txt", "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in exercises)
        with open("Answers.txt", "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in answers)
        messagebox.showinfo("完成", f"生成 {n} 道题目成功！\n文件已保存至当前目录。")
    except Exception as e:
        messagebox.showerror("错误", f"生成失败：{e}")

def grade_files():
    ex_file = filedialog.askopenfilename(title="选择 Exercises.txt", filetypes=[("Text Files", "*.txt")])
    if not ex_file:
        return
    ans_file = filedialog.askopenfilename(title="选择 Answers.txt", filetypes=[("Text Files", "*.txt")])
    if not ans_file:
        return
    try:
        grade(ex_file, ans_file)
        messagebox.showinfo("批改完成", "已生成 Grade.txt！")
    except Exception as e:
        messagebox.showerror("错误", f"批改失败：{e}")

# ========================== 界面 ==========================
root = tk.Tk()
root.title("小学四则运算题目生成器")
root.geometry("400x260")
root.resizable(False, False)

tk.Label(root, text="生成题目数量 (-n)：", font=("微软雅黑", 11)).pack(pady=5)
entry_n = tk.Entry(root, font=("Consolas", 11))
entry_n.pack()

tk.Label(root, text="数值范围 (-r)：", font=("微软雅黑", 11)).pack(pady=5)
entry_r = tk.Entry(root, font=("Consolas", 11))
entry_r.pack()

frame_btn = tk.Frame(root)
frame_btn.pack(pady=20)

tk.Button(frame_btn, text="生成题目与答案", command=generate, width=18, height=1, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=10)
tk.Button(frame_btn, text="批改答案文件", command=grade_files, width=18, height=1, bg="#2196F3", fg="white").grid(row=0, column=1, padx=10)

tk.Label(root, text="文件将自动生成在当前目录", font=("微软雅黑", 9), fg="gray").pack(pady=10)

root.mainloop()
