import os
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
from pseudo_color import convert_to_pseudo_color
from overlay import overlay_images
from merge import process_image_set, get_prefix

class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理工具")
        self.root.geometry("1200x800")
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 顶部 - 文件夹选择
        self.folder_frame = ttk.LabelFrame(self.main_frame, text="文件夹选择", padding="5")
        self.folder_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.folder_frame, text="目标文件夹:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.folder_path = tk.StringVar()
        ttk.Entry(self.folder_frame, textvariable=self.folder_path, width=80).grid(row=0, column=1, padx=5)
        ttk.Button(self.folder_frame, text="浏览", command=self.select_folder).grid(row=0, column=2, padx=5)
        
        # 中部 - 图片选择和预览区域
        # 红色通道选择和预览
        self.red_frame = ttk.LabelFrame(self.main_frame, text="红色通道", padding="5")
        self.red_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 下拉框
        self.red_combobox = ttk.Combobox(self.red_frame, width=40)
        self.red_combobox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.red_combobox.bind('<<ComboboxSelected>>', self.update_preview)
        
        # 伪彩色预览
        self.red_preview = ttk.Label(self.red_frame)
        self.red_preview.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 绿色通道选择和预览
        self.green_frame = ttk.LabelFrame(self.main_frame, text="绿色通道", padding="5")
        self.green_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # 下拉框
        self.green_combobox = ttk.Combobox(self.green_frame, width=40)
        self.green_combobox.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        self.green_combobox.bind('<<ComboboxSelected>>', self.update_preview)
        
        # 伪彩色预览
        self.green_preview = ttk.Label(self.green_frame)
        self.green_preview.grid(row=1, column=0, columnspan=2, pady=5)
        
        # 合并结果预览
        self.merge_frame = ttk.LabelFrame(self.main_frame, text="叠加结果", padding="5")
        self.merge_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.merge_preview = ttk.Label(self.merge_frame)
        self.merge_preview.grid(row=0, column=0, pady=5)
        
        # 在合并结果预览框下方添加调节控件
        self.adjust_frame = ttk.LabelFrame(self.main_frame, text="图像调节", padding="5")
        self.adjust_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 亮度调节
        ttk.Label(self.adjust_frame, text="亮度:").grid(row=0, column=0, padx=5)
        self.brightness_var = tk.DoubleVar(value=0.47)  # 修改默认值为0.47
        self.brightness_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=3.0, 
                                        variable=self.brightness_var, orient=tk.HORIZONTAL)
        self.brightness_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        self.brightness_scale.bind("<ButtonRelease-1>", self.update_preview)
        
        # 对比度调节
        ttk.Label(self.adjust_frame, text="对比度:").grid(row=0, column=2, padx=5)
        self.contrast_var = tk.DoubleVar(value=2.4)  # 修改默认值为2.4
        self.contrast_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=3.0, 
                                      variable=self.contrast_var, orient=tk.HORIZONTAL)
        self.contrast_scale.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5)
        self.contrast_scale.bind("<ButtonRelease-1>", self.update_preview)
        
        # 色彩饱和度调节
        ttk.Label(self.adjust_frame, text="饱和度:").grid(row=0, column=4, padx=5)
        self.color_var = tk.DoubleVar(value=2.33)  # 修改默认值为2.33
        self.color_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=3.0, 
                                    variable=self.color_var, orient=tk.HORIZONTAL)
        self.color_scale.grid(row=0, column=5, sticky=(tk.W, tk.E), padx=5)
        self.color_scale.bind("<ButtonRelease-1>", self.update_preview)
        
        # 背景阈值调节
        ttk.Label(self.adjust_frame, text="背景阈值:").grid(row=1, column=0, padx=5)
        self.threshold_var = tk.IntVar(value=30)  # 默认阈值30
        self.threshold_scale = ttk.Scale(self.adjust_frame, from_=0, to=255, 
                                       variable=self.threshold_var, orient=tk.HORIZONTAL)
        self.threshold_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5)
        self.threshold_scale.bind("<ButtonRelease-1>", self.update_preview)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def select_folder(self):
        """选择文件夹并自动处理"""
        folder = askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.process_folder()
    
    def process_folder(self):
        """处理选中的文件夹"""
        folder = self.folder_path.get()
        try:
            # 获取所有.bmp文件
            all_files = [f for f in os.listdir(folder) if f.endswith('.bmp')]
            print(f"找到的.bmp文件: {all_files}")  # 调试信息
            
            if not all_files:
                messagebox.showinfo("提示", "文件夹中没有找到.bmp文件")
                return
                
            # 获取所有唯一前缀
            prefixes = list(set(get_prefix(f) for f in all_files))
            print(f"找到的前缀: {prefixes}")  # 调试信息
            
            # 创建combined子文件夹
            combined_folder = os.path.join(folder, "combined")
            if not os.path.exists(combined_folder):
                os.makedirs(combined_folder)
            
            # 处理每组图片
            processed_count = 0
            for prefix in prefixes:
                print(f"正在处理前缀: {prefix}")  # 调试信息
                if process_image_set(prefix, folder):
                    processed_count += 1
                    print(f"成功处理前缀: {prefix}")  # 调试信息
            
            print(f"总共处理成功: {processed_count} 组")  # 调试信息
            
            if processed_count > 0:
                self.status_var.set(f"已合并 {processed_count} 组图片到combined文件夹")
                self.update_comboboxes()
            else:
                messagebox.showwarning("警告", "没有找到可以合并的完整图片组")
                
        except Exception as e:
            messagebox.showerror("错误", f"处理文件夹时出错: {str(e)}")
    
    def update_comboboxes(self):
        """更新下拉框中的图片列表"""
        combined_folder = os.path.join(self.folder_path.get(), "combined")
        if os.path.exists(combined_folder):
            files = [f for f in os.listdir(combined_folder) if f.endswith('.bmp')]
            self.red_combobox['values'] = files
            self.green_combobox['values'] = files
    
    def update_preview(self, event=None):
        """更新预览图片"""
        try:
            red_pseudo = None
            green_pseudo = None
            
            # 获取当前的调节值
            brightness = self.brightness_var.get()
            contrast = self.contrast_var.get()
            saturation = self.color_var.get()
            threshold = self.threshold_var.get()
            
            # 显示当前调节值
            print(f"当前参数设置 - 亮度: {brightness:.2f}, 对比度: {contrast:.2f}, "
                  f"饱和度: {saturation:.2f}, 背景阈值: {threshold}")
            self.status_var.set(f"当前参数设置 - 亮度: {brightness:.2f}, 对比度: {contrast:.2f}, "
                               f"饱和度: {saturation:.2f}, 背景阈值: {threshold}")
            
            # 更新红色通道预览
            if self.red_combobox.get():
                red_path = os.path.join(self.folder_path.get(), "combined", self.red_combobox.get())
                red_pseudo = convert_to_pseudo_color(red_path, 'red')
                self.show_preview(red_pseudo, self.red_preview, (300, 300))
            
            # 更新绿色通道预览
            if self.green_combobox.get():
                green_path = os.path.join(self.folder_path.get(), "combined", self.green_combobox.get())
                green_pseudo = convert_to_pseudo_color(green_path, 'green')
                self.show_preview(green_pseudo, self.green_preview, (300, 300))
            
            # 如果两个通道都选择了，更新合并预览
            if red_pseudo and green_pseudo:
                merged = overlay_images(red_pseudo, green_pseudo, 
                                     brightness=brightness,
                                     contrast=contrast,
                                     saturation=saturation,
                                     threshold=threshold)
                self.show_preview(merged, self.merge_preview, (300, 300))
                
        except Exception as e:
            messagebox.showerror("错误", f"更新预览时出错: {str(e)}")
    
    def show_preview(self, image_path, label, size):
        """在指定的Label中显示预览图片"""
        try:
            image = Image.open(image_path)
            image.thumbnail(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            label.configure(image=photo)
            label.image = photo  # 保持引用
        except Exception as e:
            print(f"预览图片时出错: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop() 