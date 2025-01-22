import os
import re
from PIL import Image

def get_prefix(filename):
    """提取唯一前缀的函数"""
    return re.sub(r"_(LD|LU|RD|RU)\.bmp$", "", filename)

def process_image_set(prefix, folder_path):
    """
    处理一组图片
    
    参数:
    prefix: 图片前缀
    folder_path: 源文件夹路径
    
    返回:
    bool: 处理成功返回True，否则返回False
    """
    try:
        # 创建输出子文件夹
        output_folder = os.path.join(folder_path, "combined")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # 读取该组的四张图片
        ld_image = Image.open(os.path.join(folder_path, f"{prefix}_LD.bmp"))
        lu_image = Image.open(os.path.join(folder_path, f"{prefix}_LU.bmp"))
        rd_image = Image.open(os.path.join(folder_path, f"{prefix}_RD.bmp"))
        ru_image = Image.open(os.path.join(folder_path, f"{prefix}_RU.bmp"))

        # 拼接图片
        width, height = lu_image.size
        combined_image = Image.new('RGB', (width * 2, height * 2))
        combined_image.paste(lu_image, (0, 0))
        combined_image.paste(ru_image, (width, 0))
        combined_image.paste(ld_image, (0, height))
        combined_image.paste(rd_image, (width, height))

        # 导出拼接后的图片
        output_path = os.path.join(output_folder, f"{prefix}_combined.bmp")
        combined_image.save(output_path)
        print(f"Processed and saved: {output_path}")
        return True  # 明确返回成功
        
    except Exception as e:
        print(f"Error processing prefix {prefix}: {e}")
        return False  # 明确返回失败
