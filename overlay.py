import os
from PIL import Image, ImageEnhance

def overlay_images(image1_path, image2_path, output_folder=None, alpha=0.3):
    """
    叠加两张图片
    
    参数:
    image1_path: 第一张图片路径（红色通道）
    image2_path: 第二张图片路径（绿色通道）
    output_folder: 输出文件夹路径
    alpha: 透明度，默认0.3
    """
    try:
        # 打开两张图片
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)
        
        # 确保两张图片尺寸相同
        if img1.size != img2.size:
            raise ValueError("两张图片尺寸不一致")
            
        # 转换为RGBA模式
        img1 = img1.convert('RGBA')
        img2 = img2.convert('RGBA')
        
        # 创建新图像
        width, height = img1.size
        overlay_img = Image.new('RGBA', (width, height))
        
        # 设置透明度并叠加
        for x in range(width):
            for y in range(height):
                r1, _, _, _ = img1.getpixel((x, y))
                _, g2, _, _ = img2.getpixel((x, y))
                
                # 使用透明度混合，并增加基础亮度
                r = int(r1 * alpha * 2.5)  # 增加2.5倍补偿
                g = int(g2 * alpha * 2.5)  # 增加2.5倍补偿
                # 确保值不超过255
                r = min(r, 255)
                g = min(g, 255)
                overlay_img.putpixel((x, y), (r, g, 0, 255))
        
        # 调整亮度和对比度
        overlay_img = overlay_img.convert('RGB')  # 先转换为RGB模式
        
        # 亮度调整
        brightness_enhancer = ImageEnhance.Brightness(overlay_img)
        overlay_img = brightness_enhancer.enhance(2.0)  # 增加100%的亮度
        
        # 对比度调整
        contrast_enhancer = ImageEnhance.Contrast(overlay_img)
        overlay_img = contrast_enhancer.enhance(1.3)  # 增加30%的对比度
        
        # 色彩调整
        color_enhancer = ImageEnhance.Color(overlay_img)
        overlay_img = color_enhancer.enhance(1.4)  # 增加40%的色彩饱和度
        
        # 准备输出路径
        if output_folder is None:
            output_folder = os.path.dirname(image1_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # 生成输出文件名
        name1 = os.path.splitext(os.path.basename(image1_path))[0]
        name2 = os.path.splitext(os.path.basename(image2_path))[0]
        output_path = os.path.join(output_folder, f"{name1}_{name2}_overlay.bmp")
        
        # 保存结果
        overlay_img.save(output_path)
        print(f"已生成叠加图片: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"处理图片时出错: {e}")
        return None

def batch_overlay(red_folder, green_folder, output_folder=None):
    """
    批量处理文件夹中的图片对
    
    参数:
    red_folder: 红色通道图片文件夹
    green_folder: 绿色通道图片文件夹
    output_folder: 输出文件夹路径
    """
    if output_folder is None:
        output_folder = os.path.join(os.path.dirname(red_folder), "overlay")
    
    # 获取所有图片文件名
    red_files = {os.path.splitext(f)[0].replace('_red', ''): f 
                 for f in os.listdir(red_folder) if f.endswith('.bmp')}
    green_files = {os.path.splitext(f)[0].replace('_green', ''): f 
                  for f in os.listdir(green_folder) if f.endswith('.bmp')}
    
    # 找到共同的基础文件名
    common_files = set(red_files.keys()) & set(green_files.keys())
    
    processed_count = 0
    for base_name in common_files:
        red_path = os.path.join(red_folder, red_files[base_name])
        green_path = os.path.join(green_folder, green_files[base_name])
        if overlay_images(red_path, green_path, output_folder):
            processed_count += 1
    
    print(f"批量叠加完成，共处理 {processed_count} 对图片")

if __name__ == "__main__":
    # 示例用法
    base_folder = r"E:\北京简辑\experimental\20250122四角\combined"
    red_folder = os.path.join(base_folder, "red_pseudo")
    green_folder = os.path.join(base_folder, "green_pseudo")
    
    # 批量叠加处理
    batch_overlay(red_folder, green_folder) 