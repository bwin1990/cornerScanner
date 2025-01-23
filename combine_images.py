import os
from PIL import Image
import re

def get_prefix(filename):
    """
    通过正则匹配移除 _LD、_LU、_RD、_RU 等后缀，返回文件前缀。
    """
    return re.sub(r'_(LD|LU|RD|RU)\.bmp$', '', filename, flags=re.IGNORECASE)

def process_image_set(folder_path, prefix):
    """
    读取同一组四张图片 (prefix_LD, prefix_LU, prefix_RD, prefix_RU)，
    并按照 (左上/右上；左下/右下) 的顺序拼接后保存到 combined 子文件夹。
    """
    ld_path = os.path.join(folder_path, prefix + "_LD.bmp")
    lu_path = os.path.join(folder_path, prefix + "_LU.bmp")
    rd_path = os.path.join(folder_path, prefix + "_RD.bmp")
    ru_path = os.path.join(folder_path, prefix + "_RU.bmp")

    ld_img = Image.open(ld_path)
    lu_img = Image.open(lu_path)
    rd_img = Image.open(rd_path)
    ru_img = Image.open(ru_path)

    w1, h1 = lu_img.size
    w2, h2 = ru_img.size
    w3, h3 = ld_img.size
    w4, h4 = rd_img.size

    total_width = w1 + w2
    total_height = h1 + h3

    combined_img = Image.new("RGB", (total_width, total_height))
    combined_img.paste(lu_img, (0, 0))
    combined_img.paste(ru_img, (w1, 0))
    combined_img.paste(ld_img, (0, h1))
    combined_img.paste(rd_img, (w3, h2))

    # 创建或使用"combined"子文件夹
    combined_folder = os.path.join(folder_path, "combined")
    if not os.path.exists(combined_folder):
        os.makedirs(combined_folder)

    output_path = os.path.join(combined_folder, prefix + "_combined.bmp")
    combined_img.save(output_path)

def main(folder_path):
    # 获取所有 bmp 文件
    all_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".bmp")]

    # 提取所有前缀并去重
    prefixes = set(get_prefix(f) for f in all_files)

    # 逐一处理对应的四张图片
    for prefix in prefixes:
        process_image_set(folder_path, prefix)
    
    # 返回 combined 文件夹路径
    return os.path.join(folder_path, "combined")

if __name__ == "__main__":
    # 使用 tkinter 弹出对话框选择文件夹
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    folderPath = filedialog.askdirectory(title="请选择一个包含 BMP 图片的文件夹")
    if folderPath:
        combined_path = main(folderPath)
        # 启动图像叠加工具
        ImageBlender(combined_path)