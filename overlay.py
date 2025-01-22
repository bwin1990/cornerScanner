import os
from PIL import Image, ImageEnhance, ImageOps

def overlay_images(image1_path, image2_path, output_folder=None, alpha=0.3,
                  brightness=0.47, contrast=2.4, saturation=2.33, threshold=30):
    """
    叠加两张图片，在叠加前先进行反相处理
    
    参数:
    image1_path: 第一张图片路径（红色通道）
    image2_path: 第二张图片路径（绿色通道）
    output_folder: 输出文件夹路径
    alpha: 透明度，默认0.3
    brightness: 亮度增强系数，默认0.47
    contrast: 对比度增强系数，默认2.4
    saturation: 色彩饱和度增强系数，默认2.33
    threshold: 背景过滤阈值，默认30
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
        
        # 对每个像素进行处理
        for x in range(width):
            for y in range(height):
                r1, _, _, _ = img1.getpixel((x, y))
                _, g2, _, _ = img2.getpixel((x, y))
                
                # 在各自通道内进行反相
                r = 255 - r1  # 红色通道反相
                g = 255 - g2  # 绿色通道反相
                
                # 使用透明度混合
                r = int(r * alpha * 2.5)
                g = int(g * alpha * 2.5)
                
                # 确保值不超过255
                r = min(r, 255)
                g = min(g, 255)
                
                # 如果两个通道都低于阈值，则设置为透明
                if r < threshold and g < threshold:
                    overlay_img.putpixel((x, y), (0, 0, 0, 0))  # 完全透明
                else:
                    overlay_img.putpixel((x, y), (r, g, 0, 255))
        
        # 调整亮度和对比度
        # 由于我们需要保持透明通道，先分离通道
        r, g, b, a = overlay_img.split()
        rgb_img = Image.merge('RGB', (r, g, b))
        
        # 亮度调整
        brightness_enhancer = ImageEnhance.Brightness(rgb_img)
        rgb_img = brightness_enhancer.enhance(brightness)
        
        # 对比度调整
        contrast_enhancer = ImageEnhance.Contrast(rgb_img)
        rgb_img = contrast_enhancer.enhance(contrast)
        
        # 色彩调整
        color_enhancer = ImageEnhance.Color(rgb_img)
        rgb_img = color_enhancer.enhance(saturation)
        
        # 重新合并透明通道
        r, g, b = rgb_img.split()
        overlay_img = Image.merge('RGBA', (r, g, b, a))
        
        # 准备输出路径
        if output_folder is None:
            output_folder = os.path.dirname(image1_path)
            
        # 生成输出文件名
        name1 = os.path.splitext(os.path.basename(image1_path))[0]
        name2 = os.path.splitext(os.path.basename(image2_path))[0]
        output_path = os.path.join(output_folder, f"{name1}_{name2}_overlay.bmp")
        
        # 保存结果
        overlay_img.save(output_path)
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
    try:
        # 检查输入文件夹是否存在
        if not os.path.exists(red_folder):
            raise FileNotFoundError(f"红色通道文件夹不存在: {red_folder}")
        if not os.path.exists(green_folder):
            raise FileNotFoundError(f"绿色通道文件夹不存在: {green_folder}")
            
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
        return processed_count
        
    except Exception as e:
        print(f"批量处理时出错: {e}")
        return 0