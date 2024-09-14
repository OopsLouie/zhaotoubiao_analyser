import os
import errno
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
from csv_utils import *
from request_utils import *
from datetime import datetime

try:
    from version import version_str
except:
    version_str = "debug"

def show_warning(msg):
    messagebox.showwarning("警告", msg)

def center_window(root, width, height):
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口居中位置
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    # 设置窗口位置
    root.geometry(f'{width}x{height}+{x}+{y}')

def select_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        path_entry.config(state=tk.NORMAL)
        path_entry.delete(0, tk.END)
        path_entry.insert(0, file_path)
        path_entry.config(state=tk.DISABLED)

def analyse():
    threading.Thread(target=analyse_internal).start()

def get_url_result(url, keywords):
    content = fetch_page_content(url)
    # 错误处理
    if "请求出现超时" in content:
        log_message(content)
        return -1, "请求出现超时", ""
    elif "请求出现错误" in content:
        log_message(content)
        return -2, "请求出现错误", content
    # 查找
    for key in keywords:
        if key in content:
            log_message("找到"+key)
            return 1, "找到"+key, content
    else:
        log_message("未找到")
        return 0, "未找到", ""

def analyse_internal():
    input_file = path_entry.get()
    if not input_file:
        show_warning("先选择输入文件")
        return
    output_file_name = editable_entry.get()
    if not output_file_name:
        show_warning("输出文件名不得为空")
        return
    now = datetime.now()
    current_time_text = now.strftime("%Y-%m-%d-%H-%M-%S")
    output_file_path = "/".join(input_file.split('/')[:-1]) + "/" + output_file_name + "_" + current_time_text + ".csv"
    content = text_widget.get("1.0", tk.END)
    lines = content.splitlines()
    keywords = []
    for line in lines:
        if len(line) != 0 and not line.isspace():
            keywords.append(line)
    if len(keywords) == 0:
        show_warning("请填入关键词, 一行一个")
        return
    try:
        urls = read_first_column(input_file)
    except Exception as e:
        show_warning(e)
        return
    results_http = []
    results_https = []
    sz = len(urls)
    for i in range(sz):
        url = urls[i]
        log_message(f"=========== 正在处理{i+1}/{sz} ===========")
        log_message(f"url: {url}")

        try_url = "http://" + url
        log_message("尝试http访问:")
        rc, result, content = get_url_result(try_url, keywords)
        results_http.append(result)

        if (rc < 0):
            try_url = "https://" + url
            log_message("尝试https访问:")
            rc, result, content = get_url_result(try_url, keywords)
            results_https.append(result)
        else:
            results_https.append("无需爬取")

    final_results=[]
    for i in range(sz):
        result_1 = results_http[i]
        result_2 = results_https[i]
        if result_1.startswith("找到") or result_2.startswith("找到"):
            final_results.append("找到")
        elif "未找到" in result_1 or "未找到" in result_2:
            final_results.append("未找到")
        else:
            final_results.append("其他结果")
    urls.insert(0, "url")
    results_http.insert(0, "http访问结果")
    results_https.insert(0, "https访问结果")
    final_results.insert(0, "汇总结果")

    write_lists_to_csv(output_file_path, urls, results_http, results_https, final_results)
    log_message("分析完毕")
    log_message("文件保存到:" + output_file_path)

def log_message(message):
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, message + '\n')
    log_text.config(state=tk.DISABLED)
    log_text.yview(tk.END)

root = tk.Tk()
root.title("爬取分析软件 " + version_str)
center_window(root, 800, 800)
root.resizable(0,0)

frame = tk.Frame(root)
frame.pack(pady=10)

path_label = tk.Label(frame, text="输入文件路径:")
path_label.grid(row=0, column=0, padx=5, sticky='w')
path_entry = tk.Entry(frame, width=50, state=tk.DISABLED)
path_entry.grid(row=0, column=1, padx=5)

editable_label = tk.Label(frame, text="输出文件名:")
editable_label.grid(row=1, column=0, padx=5, sticky='w')
editable_entry = tk.Entry(frame, width=50)
editable_entry.insert(0, "result")
editable_entry.grid(row=1, column=1, padx=5)

bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10, fill=tk.X)
select_button = tk.Button(bottom_frame, text="选择文件", command=select_file)
select_button.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
analyse_button = tk.Button(bottom_frame, text="爬取分析", command=analyse)
analyse_button.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')
bottom_frame.grid_columnconfigure(0, weight=1)
bottom_frame.grid_columnconfigure(1, weight=1)

tk.Label(root, text="关键词:").pack(pady=0, padx=0, anchor='w')
text_widget = tk.Text(root, width=80, height=10, wrap=tk.WORD)
text_widget.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

tk.Label(root, text="日志:").pack(pady=0, padx=0, anchor='w')
log_text = scrolledtext.ScrolledText(root, width=80, height=20, wrap=tk.WORD, state=tk.DISABLED)
log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

root.mainloop()
