import os
from PIL import Image

def convert_to_pseudo_color(image_path, color_mode='red', output_folder=None):
    """
    将图片转换为伪彩色图片
    
    参数:
    image_path: 输入图片路径
    color_mode: 'red' 或 'green'，选择伪彩色模式
    output_folder: 输出文件夹路径，如果为None则使用源文件夹
    """
    try:
        # 打开图片并转换为灰度图
        img = Image.open(image_path)
        gray_img = img.convert('L')
        
        # 创建新的RGB图像
        pseudo_img = Image.new('RGB', gray_img.size)
        width, height = gray_img.size
        
        # 逐像素处理
        for x in range(width):
            for y in range(height):
                gray_value = gray_img.getpixel((x, y))
                if color_mode == 'red':
                    pseudo_img.putpixel((x, y), (gray_value, 0, 0))
                else:  # green
                    pseudo_img.putpixel((x, y), (0, gray_value, 0))
        
        # 准备输出路径
        if output_folder is None:
            output_folder = os.path.dirname(image_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # 生成输出文件名
        filename = os.path.basename(image_path)
        name, ext = os.path.splitext(filename)
        output_path = os.path.join(output_folder, f"{name}_{color_mode}{ext}")
        
        # 保存结果
        pseudo_img.save(output_path)
        print(f"已生成伪彩色图片: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return None

def batch_process(input_folder, color_mode='red', output_folder=None):
    """
    批量处理文件夹中的所有图片
    
    参数:
    input_folder: 输入文件夹路径
    color_mode: 'red' 或 'green'，选择伪彩色模式
    output_folder: 输出文件夹路径
    """
    if output_folder is None:
        output_folder = os.path.join(input_folder, f"{color_mode}_pseudo")
    
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # 处理所有图片
    processed_count = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.bmp', '.jpg', '.png')):
            image_path = os.path.join(input_folder, filename)
            if convert_to_pseudo_color(image_path, color_mode, output_folder):
                processed_count += 1
    
    print(f"批量处理完成，共处理 {processed_count} 张图片")

if __name__ == "__main__":
    # 示例用法
    folder_path = r"E:\北京简辑\experimental\20250122四角\combined"  # 使用合并后的图片文件夹
    
    # 批量生成红色伪彩图
    batch_process(folder_path, 'red')
    
    # 批量生成绿色伪彩图
    batch_process(folder_path, 'green') 