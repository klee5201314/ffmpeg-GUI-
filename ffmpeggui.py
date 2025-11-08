import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from ncmdump import dump
import subprocess
import os
import sys
import threading
import json
import platform
import time
import re

class SplashScreen:
    """启动界面，显示硬件检测进度"""
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg GUI")
        self.root.geometry("400x200")
        self.root.configure(bg="#f0f0f0")
        
        # 居中显示
        window_width = 400
        window_height = 200
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 禁止调整大小
        self.root.resizable(False, False)
        
        # 移除窗口装饰（可选）
        # self.root.overrideredirect(True)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置启动界面UI"""
        # 标题
        title_label = ttk.Label(
            self.root, 
            text="🎬 FFmpeg 媒体处理工具", 
            font=("Arial", 16, "bold"),
            background="#f0f0f0"
        )
        title_label.pack(pady=20)
        
        # 版本信息
        version_label = ttk.Label(
            self.root, 
            text="版本 V0.1", 
            font=("Arial", 10),
            background="#f0f0f0"
        )
        version_label.pack(pady=5)
        
        # 状态标签
        self.status_label = ttk.Label(
            self.root, 
            text="正在检测硬件加速支持...", 
            font=("Arial", 10),
            background="#f0f0f0"
        )
        self.status_label.pack(pady=10)
        
        # 进度条
        self.progress = ttk.Progressbar(
            self.root, 
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        self.progress.start()
        
        # 版权信息
        copyright_label = ttk.Label(
            self.root, 
            text="© 2024 FFmpeg GUI Tool", 
            font=("Arial", 8),
            background="#f0f0f0"
        )
        copyright_label.pack(side="bottom", pady=10)
    
    def update_status(self, text):
        """更新状态文本"""
        self.status_label.config(text=text)
        self.root.update()
    
    def close(self):
        """关闭启动界面"""
        self.root.destroy()

class FFmpegGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 FFmpeg 媒体处理工具")
        # 设置为16:9比例 (1280x720)
        self.root.geometry("1280x720")
        self.root.configure(bg="#f0f0f0")
        self.root.minsize(1024, 576)  # 最小尺寸保持16:9
        
        # 版本信息
        self.version = "V0.1"
        
        # 当前语言
        self.current_language = "zh_CN"  # 默认中文
        
        # 硬件加速支持
        self.hardware_acceleration = {}
        
        # 硬件编码器支持
        self.hardware_encoders = {}
        
        # 加载语言资源
        self.load_language_resources()
        
        # 设置样式
        self.setup_styles()
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.is_processing = False
        self.ffmpeg_process = None
        
        # 进度跟踪变量
        self.progress_var = tk.DoubleVar()
        self.progress_percent = tk.StringVar(value="0%")
        self.waiting_for_completion = False
        self.progress_check_count = 0
        
        # 显示启动界面
        self.splash = SplashScreen(tk.Toplevel(root))
        self.root.withdraw()  # 隐藏主窗口
        
        # 在后台线程中初始化
        self.init_thread = threading.Thread(target=self.initialize_app)
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # 检查初始化状态
        self.check_initialization()
    
    def check_initialization(self):
        """检查初始化状态"""
        if self.init_thread.is_alive():
            self.root.after(100, self.check_initialization)
        else:
            # 初始化完成，显示主窗口
            self.splash.close()
            self.root.deiconify()  # 显示主窗口
            self.create_widgets()

    def check_ncmdump(self):
        """检查ncmdump是否可用"""
        try:
            from ncmdump import dump
            return True
        except ImportError:
            return False
        
    def initialize_app(self):
        """初始化应用程序"""
        # 更新启动界面状态
        self.splash.update_status("正在检查 FFmpeg...")
        
        # 检查FFmpeg
        if not self.check_ffmpeg():
            return
        
        # 更新启动界面状态
        self.splash.update_status("正在检测硬件加速支持...")
        
        # 检查ncmdump
        self.ncmdump_available = self.check_ncmdump()
        
        # 检测硬件加速
        self.detect_hardware_acceleration()
        
        # 更新启动界面状态
        self.splash.update_status("正在检测硬件编码器...")
        
        # 检测硬件编码器
        self.detect_hardware_encoders()
        
        # 模拟检测过程（实际检测很快，这里只是为了演示）
        time.sleep(1)
        
        # 更新启动界面状态
        self.splash.update_status("初始化完成，启动主界面...")
        time.sleep(0.5)
    
    def load_language_resources(self):
        """加载语言资源文件"""
        self.languages = {
            "zh_CN": {
                "title": "🎬 FFmpeg 媒体处理工具",
                "file_operations": "📁 文件操作",
                "source_file": "📄 源文件:",
                "output_file": "💾 输出文件:",
                "browse": "🔍 浏览",
                "file_info": "📊 文件信息",
                "command_preview": "⚙️ 命令预览",
                "update_preview": "🔄 更新预览",
                "start_processing": "🚀 开始处理",
                "ready": "✅ 就绪",
                "processing": "⏳ 处理中...",
                "completed": "🎉 处理完成!",
                "failed": "❌ 处理失败",
                "format_conversion": "🔄 格式转换",
                "output_format": "📄 输出格式:",
                "convert_format": "🔄 转换格式",
                "quality_settings": "⭐ 质量设置",
                "video_quality": "🎥 视频质量:",
                "audio_quality": "🎵 音频质量:",
                "high_quality": "高质量",
                "medium_quality": "中等",
                "low_quality": "低质量",
                "original_quality": "原质量",
                "quick_actions": "⚡ 快速操作",
                "extract_audio": "🎵 提取音频",
                "extract_video": "🎥 提取视频",
                "compress_media": "📦 压缩媒体",
                "video_encoding": "🎬 视频编码",
                "video_encoder": "🔧 视频编码器:",
                "resolution": "📐 分辨率:",
                "fps": "🎞️ 帧率:",
                "original_resolution": "原分辨率",
                "original_fps": "原帧率",
                "video_filters": "🎨 视频滤镜",
                "crop_video": "✂️ 裁剪视频",
                "crop_params": "📏 裁剪参数:",
                "scale_video": "📏 缩放视频",
                "rotate_video": "🔄 旋转视频",
                "rotate_angle": "📐 旋转角度:",
                "apply_video_processing": "🎬 应用视频处理",
                "audio_settings": "🎵 音频设置",
                "audio_encoder": "🔊 音频编码器:",
                "sample_rate": "🎚️ 采样率:",
                "channels": "🔊 声道数:",
                "bitrate": "📊 比特率:",
                "audio_filters": "🎛️ 音频滤镜",
                "adjust_volume": "🔊 调整音量",
                "volume_factor": "📢 音量倍数:",
                "apply_audio_processing": "🎵 应用音频处理",
                "custom_parameters": "🔧 自定义参数",
                "ffmpeg_parameters": "⚙️ FFmpeg参数:",
                "example": "📝 示例: -crf 23 -preset medium -c:a copy",
                "run_custom_command": "🚀 运行自定义命令",
                "preset_configs": "🎛️ 预设配置",
                "no_preset": "无",
                "high_quality_mp4": "高质量MP4",
                "high_quality_mp3": "高质量MP3",
                "web_optimized": "网页优化",
                "mobile_optimized": "移动设备优化",
                "settings": "⚙️ 设置",
                "language_settings": "🌐 语言设置",
                "switch_to_english": "🇺🇸 Switch to English",
                "switch_to_chinese": "🇨🇳 切换到中文",
                "hardware_acceleration": "🚀 硬件加速",
                "hardware_accel_settings": "⚡ 硬件加速设置",
                "hwaccel_none": "❌ 无硬件加速",
                "hwaccel_cuda": "🎮 NVIDIA CUDA",
                "hwaccel_qsv": "🔵 Intel Quick Sync",
                "hwaccel_vaapi": "🔴 VA-API",
                "hwaccel_d3d11va": "🟢 Direct3D 11",
                "hwaccel_videotoolbox": "🍎 Apple VideoToolbox",
                "hwaccel_amf": "🟣 AMD AMF",
                "detect_hardware": "🔍 检测硬件加速",
                "hardware_detection": "🔧 硬件检测",
                "hardware_status": "📊 硬件状态",
                "hardware_encoders": "🔧 硬件编码器",
                "version_info": "ℹ️ 版本信息",
                "current_version": "当前版本:",
                "re_detect": "🔄 重新检测",
                "detection_completed": "✅ 检测完成",
                "detection_failed": "❌ 检测失败",
                "no_hardware_support": "❌ 无硬件加速支持",
                "hardware_support_detected": "✅ 检测到硬件加速支持",
                "error": "❌ 错误",
                "success": "✅ 成功",
                "select_input_output": "⚠️ 请选择输入和输出文件",
                "select_input_file": "⚠️ 请选择输入文件",
                "ffmpeg_not_found": "❌ FFmpeg未安装",
                "installation_guide": "📖 FFmpeg安装指南",
                "progress": "📊 进度",
                "estimated_time": "⏱️ 预计剩余时间",
                "processing_file": "📁 处理文件",
                "waiting_finalization": "⏳ 请稍等，正在打包文件...",
                "finalizing": "📦 正在完成处理...",
                "finalizing_processing": "⏳ 正在完成处理..."
            },
            "en_US": {
                "title": "🎬 FFmpeg Media Processing Tool",
                "file_operations": "📁 File Operations",
                "source_file": "📄 Source File:",
                "output_file": "💾 Output File:",
                "browse": "🔍 Browse",
                "file_info": "📊 File Information",
                "command_preview": "⚙️ Command Preview",
                "update_preview": "🔄 Update Preview",
                "start_processing": "🚀 Start Processing",
                "ready": "✅ Ready",
                "processing": "⏳ Processing...",
                "completed": "🎉 Processing Completed!",
                "failed": "❌ Processing Failed",
                "format_conversion": "🔄 Format Conversion",
                "output_format": "📄 Output Format:",
                "convert_format": "🔄 Convert Format",
                "quality_settings": "⭐ Quality Settings",
                "video_quality": "🎥 Video Quality:",
                "audio_quality": "🎵 Audio Quality:",
                "high_quality": "High Quality",
                "medium_quality": "Medium",
                "low_quality": "Low Quality",
                "original_quality": "Original Quality",
                "quick_actions": "⚡ Quick Actions",
                "extract_audio": "🎵 Extract Audio",
                "extract_video": "🎥 Extract Video",
                "compress_media": "📦 Compress Media",
                "video_encoding": "🎬 Video Encoding",
                "video_encoder": "🔧 Video Encoder:",
                "resolution": "📐 Resolution:",
                "fps": "🎞️ Frame Rate:",
                "original_resolution": "Original Resolution",
                "original_fps": "Original FPS",
                "video_filters": "🎨 Video Filters",
                "crop_video": "✂️ Crop Video",
                "crop_params": "📏 Crop Parameters:",
                "scale_video": "📏 Scale Video",
                "rotate_video": "🔄 Rotate Video",
                "rotate_angle": "📐 Rotation Angle:",
                "apply_video_processing": "🎬 Apply Video Processing",
                "audio_settings": "🎵 Audio Settings",
                "audio_encoder": "🔊 Audio Encoder:",
                "sample_rate": "🎚️ Sample Rate:",
                "channels": "🔊 Channels:",
                "bitrate": "📊 Bitrate:",
                "audio_filters": "🎛️ Audio Filters",
                "adjust_volume": "🔊 Adjust Volume",
                "volume_factor": "📢 Volume Factor:",
                "apply_audio_processing": "🎵 Apply Audio Processing",
                "custom_parameters": "🔧 Custom Parameters",
                "ffmpeg_parameters": "⚙️ FFmpeg Parameters:",
                "example": "📝 Example: -crf 23 -preset medium -c:a copy",
                "run_custom_command": "🚀 Run Custom Command",
                "preset_configs": "🎛️ Preset Configurations",
                "no_preset": "None",
                "high_quality_mp4": "High Quality MP4",
                "high_quality_mp3": "High Quality MP3",
                "web_optimized": "Web Optimized",
                "mobile_optimized": "Mobile Optimized",
                "settings": "⚙️ Settings",
                "language_settings": "🌐 Language Settings",
                "switch_to_english": "🇺🇸 Switch to English",
                "switch_to_chinese": "🇨🇳 切换到中文",
                "hardware_acceleration": "🚀 Hardware Acceleration",
                "hardware_accel_settings": "⚡ Hardware Acceleration Settings",
                "hwaccel_none": "❌ No Hardware Acceleration",
                "hwaccel_cuda": "🎮 NVIDIA CUDA",
                "hwaccel_qsv": "🔵 Intel Quick Sync",
                "hwaccel_vaapi": "🔴 VA-API",
                "hwaccel_d3d11va": "🟢 Direct3D 11",
                "hwaccel_videotoolbox": "🍎 Apple VideoToolbox",
                "hwaccel_amf": "🟣 AMD AMF",
                "detect_hardware": "🔍 Detect Hardware Acceleration",
                "hardware_detection": "🔧 Hardware Detection",
                "hardware_status": "📊 Hardware Status",
                "hardware_encoders": "🔧 Hardware Encoders",
                "version_info": "ℹ️ Version Information",
                "current_version": "Current Version:",
                "re_detect": "🔄 Re-detect",
                "detection_completed": "✅ Detection Completed",
                "detection_failed": "❌ Detection Failed",
                "no_hardware_support": "❌ No Hardware Acceleration Support",
                "hardware_support_detected": "✅ Hardware Acceleration Support Detected",
                "error": "❌ Error",
                "success": "✅ Success",
                "select_input_output": "⚠️ Please select input and output files",
                "select_input_file": "⚠️ Please select input file",
                "ffmpeg_not_found": "❌ FFmpeg not installed",
                "installation_guide": "📖 FFmpeg Installation Guide",
                "progress": "📊 Progress",
                "estimated_time": "⏱️ Estimated Time Remaining",
                "processing_file": "📁 Processing File",
                "waiting_finalization": "⏳ Please wait, finalizing file...",
                "finalizing": "📦 Finalizing processing...",
                "finalizing_processing": "⏳ Finalizing processing..."
            }
        }
    
    def t(self, key):
        """翻译文本"""
        return self.languages[self.current_language].get(key, key)
    
    def switch_language(self, language):
        """切换语言"""
        self.current_language = language
        self.update_ui_text()
    
    def update_ui_text(self):
        """更新UI文本"""
        # 更新窗口标题
        self.root.title(self.t("title"))
        
        # 更新文件操作区域
        self.file_operations_frame.configure(text=self.t("file_operations"))
        self.source_file_label.configure(text=self.t("source_file"))
        self.output_file_label.configure(text=self.t("output_file"))
        self.input_browse_button.configure(text=self.t("browse"))
        self.output_browse_button.configure(text=self.t("browse"))
        
        # 更新文件信息区域
        self.file_info_frame.configure(text=self.t("file_info"))
        
        # 更新命令预览区域
        self.command_preview_frame.configure(text=self.t("command_preview"))
        self.update_preview_button.configure(text=self.t("update_preview"))
        self.process_btn.configure(text=self.t("start_processing"))
        self.status_label.configure(text=self.t("ready"))
        
        # 更新标签页文本
        self.notebook.tab(0, text="🔄 " + self.t("format_conversion").replace("🔄 ", ""))
        self.notebook.tab(1, text="🎬 " + self.t("video_encoding").replace("🎬 ", ""))
        self.notebook.tab(2, text="🎵 " + self.t("audio_settings").replace("🎵 ", ""))
        self.notebook.tab(3, text="🔧 " + self.t("custom_parameters").replace("🔧 ", ""))
        self.notebook.tab(4, text="⚙️ " + self.t("settings").replace("⚙️ ", ""))
        
        # 更新基础标签页
        self.convert_frame.configure(text=self.t("format_conversion"))
        self.output_format_label.configure(text=self.t("output_format"))
        self.convert_button.configure(text=self.t("convert_format"))
        
        self.quality_frame.configure(text=self.t("quality_settings"))
        self.video_quality_label.configure(text=self.t("video_quality"))
        self.audio_quality_label.configure(text=self.t("audio_quality"))
        
        # 更新质量选项
        qualities = [self.t("high_quality"), self.t("medium_quality"), 
                     self.t("low_quality"), self.t("original_quality")]
        self.video_quality_combo.configure(values=qualities)
        self.audio_quality_combo.configure(values=qualities)
        
        self.quick_frame.configure(text=self.t("quick_actions"))
        self.extract_audio_button.configure(text=self.t("extract_audio"))
        self.extract_video_button.configure(text=self.t("extract_video"))
        self.compress_media_button.configure(text=self.t("compress_media"))
        
        # 更新视频标签页
        self.video_encoding_frame.configure(text=self.t("video_encoding"))
        self.video_encoder_label.configure(text=self.t("video_encoder"))
        self.resolution_label.configure(text=self.t("resolution"))
        self.fps_label.configure(text=self.t("fps"))
        
        resolutions = [self.t("original_resolution"), "3840x2160", "1920x1080", 
                      "1280x720", "854x480", "640x360"]
        self.resolution_combo.configure(values=resolutions)
        
        fps_values = [self.t("original_fps"), "60", "30", "25", "24", "15"]
        self.fps_combo.configure(values=fps_values)
        
        self.video_filters_frame.configure(text=self.t("video_filters"))
        self.crop_video_check.configure(text=self.t("crop_video"))
        self.crop_params_label.configure(text=self.t("crop_params"))
        self.scale_video_check.configure(text=self.t("scale_video"))
        self.rotate_video_check.configure(text=self.t("rotate_video"))
        self.rotate_angle_label.configure(text=self.t("rotate_angle"))
        self.apply_video_processing_button.configure(text=self.t("apply_video_processing"))
        
        # 更新音频标签页
        self.audio_settings_frame.configure(text=self.t("audio_settings"))
        self.audio_encoder_label.configure(text=self.t("audio_encoder"))
        self.sample_rate_label.configure(text=self.t("sample_rate"))
        self.channels_label.configure(text=self.t("channels"))
        self.bitrate_label.configure(text=self.t("bitrate"))
        
        channels = ["1", "2", self.t("original_quality").replace("质量", "声道")]
        self.channels_combo.configure(values=channels)
        
        self.audio_filters_frame.configure(text=self.t("audio_filters"))
        self.adjust_volume_check.configure(text=self.t("adjust_volume"))
        self.volume_factor_label.configure(text=self.t("volume_factor"))
        self.apply_audio_processing_button.configure(text=self.t("apply_audio_processing"))
        
        # 更新高级标签页
        self.custom_parameters_frame.configure(text=self.t("custom_parameters"))
        self.ffmpeg_parameters_label.configure(text=self.t("ffmpeg_parameters"))
        self.example_label.configure(text=self.t("example"))
        self.run_custom_command_button.configure(text=self.t("run_custom_command"))
        
        self.preset_configs_frame.configure(text=self.t("preset_configs"))
        presets = [self.t("no_preset"), self.t("high_quality_mp4"), 
                  self.t("high_quality_mp3"), self.t("web_optimized"), 
                  self.t("mobile_optimized")]
        self.preset_combo.configure(values=presets)
        
        # 更新设置标签页
        self.language_frame.configure(text=self.t("language_settings"))
        if self.current_language == "zh_CN":
            self.switch_to_english_button.configure(text=self.t("switch_to_english"))
        else:
            self.switch_to_chinese_button.configure(text=self.t("switch_to_chinese"))
        
        self.hardware_accel_frame.configure(text=self.t("hardware_accel_settings"))
        self.hardware_detection_label.configure(text=self.t("hardware_detection"))
        self.hardware_status_label.configure(text=self.t("hardware_status"))
        self.hardware_encoders_label.configure(text=self.t("hardware_encoders"))
        self.detect_hardware_button.configure(text=self.t("re_detect"))
        
        self.version_frame.configure(text=self.t("version_info"))
        self.current_version_label.configure(text=self.t("current_version") + " " + self.version)
        
        # 更新进度标签
        if hasattr(self, 'progress_label'):
            self.progress_label.configure(text=self.t("progress"))
        
        # 更新等待信息
        if hasattr(self, 'waiting_label'):
            self.waiting_label.configure(text=self.t("finalizing_processing"))
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 16, "bold"), background="#f0f0f0")
        style.configure("Section.TLabelframe", font=("Arial", 10, "bold"))
        style.configure("Section.TLabelframe.Label", font=("Arial", 10, "bold"))
        style.configure("Action.TButton", font=("Arial", 10, "bold"), padding=5)
        style.configure("Primary.TButton", font=("Arial", 10, "bold"), padding=8)
    
    def detect_hardware_acceleration(self):
        """检测硬件加速支持"""
        self.hardware_acceleration = {}
        
        # 检测可用的硬件加速器
        hwaccels_to_check = {
            "cuda": "🎮 NVIDIA CUDA",
            "qsv": "🔵 Intel Quick Sync", 
            "vaapi": "🔴 VA-API",
            "d3d11va": "🟢 Direct3D 11",
            "videotoolbox": "🍎 Apple VideoToolbox",
            "amf": "🟣 AMD AMF"
        }
        
        try:
            # 运行ffmpeg -hwaccels获取支持的硬件加速器
            result = subprocess.run(
                ["ffmpeg", "-hwaccels"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            output = result.stdout.lower()
            
            for hwaccel, display_name in hwaccels_to_check.items():
                if hwaccel in output:
                    self.hardware_acceleration[hwaccel] = {
                        "name": display_name,
                        "supported": True
                    }
                else:
                    self.hardware_acceleration[hwaccel] = {
                        "name": display_name,
                        "supported": False
                    }
                    
        except Exception as e:
            print(f"硬件加速检测失败: {e}")
            # 如果检测失败，将所有硬件加速标记为不支持
            for hwaccel, display_name in hwaccels_to_check.items():
                self.hardware_acceleration[hwaccel] = {
                    "name": display_name,
                    "supported": False
                }
    
    def detect_hardware_encoders(self):
        """检测硬件编码器支持"""
        self.hardware_encoders = {}
        
        # 硬件编码器映射
        encoder_mapping = {
            "h264_nvenc": "NVIDIA H.264",
            "hevc_nvenc": "NVIDIA H.265",
            "h264_qsv": "Intel H.264",
            "hevc_qsv": "Intel H.265",
            "h264_amf": "AMD H.264",
            "hevc_amf": "AMD H.265",
            "h264_vaapi": "VA-API H.264",
            "hevc_vaapi": "VA-API H.265",
            "h264_videotoolbox": "VideoToolbox H.264",
            "hevc_videotoolbox": "VideoToolbox H.265"
        }
        
        try:
            # 运行ffmpeg -encoders获取支持的编码器
            result = subprocess.run(
                ["ffmpeg", "-encoders"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            output = result.stdout
            
            for encoder, display_name in encoder_mapping.items():
                if re.search(rf"^\s*V\S*\s+{encoder}", output, re.MULTILINE):
                    self.hardware_encoders[encoder] = {
                        "name": display_name,
                        "supported": True
                    }
                else:
                    self.hardware_encoders[encoder] = {
                        "name": display_name,
                        "supported": False
                    }
                    
        except Exception as e:
            print(f"硬件编码器检测失败: {e}")
            # 如果检测失败，将所有硬件编码器标记为不支持
            for encoder, display_name in encoder_mapping.items():
                self.hardware_encoders[encoder] = {
                    "name": display_name,
                    "supported": False
                }
    
    def check_ffmpeg(self):
        """检查FFmpeg是否安装"""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
            version = result.stdout.split('\n')[0]
            print(f"FFmpeg版本: {version}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.show_installation_guide()
            return False
    
    def show_installation_guide(self):
        """显示FFmpeg安装指南"""
        install_window = tk.Toplevel(self.root)
        install_window.title(self.t("ffmpeg_not_found"))
        install_window.geometry("600x500")
        install_window.configure(bg="#f0f0f0")
        
        title = ttk.Label(install_window, text=self.t("installation_guide"), style="Title.TLabel")
        title.pack(pady=10)
        
        guide_text = """
        FFmpeg 未安装或未在系统PATH中找到。
        
        Windows系统:
        1. 访问 https://ffmpeg.org/download.html
        2. 下载Windows版本压缩包
        3. 解压到 C:\\\\ffmpeg 目录
        4. 将 C:\\\\ffmpeg\\\\bin 添加到系统PATH环境变量
        5. 重新启动命令提示符并验证安装: ffmpeg -version
        
        macOS系统:
        1. 使用Homebrew安装: brew install ffmpeg
        
        Linux系统:
        1. Ubuntu/Debian: sudo apt install ffmpeg
        2. CentOS/RHEL: sudo yum install ffmpeg
        3. Arch Linux: sudo pacman -S ffmpeg
        
        验证安装: 在终端运行 ffmpeg -version
        """
        
        text_widget = scrolledtext.ScrolledText(install_window, wrap="word", padx=10, pady=10, width=70, height=20)
        text_widget.insert("1.0", guide_text)
        text_widget.config(state="disabled")
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        close_btn = ttk.Button(install_window, text="关闭", command=install_window.destroy, style="Action.TButton")
        close_btn.pack(pady=10)
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主框架和滚动条
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
        # 创建滚动条
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side="right", fill="y")
    
        # 创建画布
        canvas = tk.Canvas(main_frame, yscrollcommand=scrollbar.set, bg="#f0f0f0")
        canvas.pack(side="left", fill="both", expand=True)
    
        # 配置滚动条
        scrollbar.config(command=canvas.yview)
    
        # 创建内部框架
        self.inner_frame = ttk.Frame(canvas)
        self.inner_frame_id = canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
    
        # 配置画布滚动
        def configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(self.inner_frame_id, width=event.width)
    
        self.inner_frame.bind("<Configure>", configure_canvas)
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(self.inner_frame_id, width=e.width))
    
        # 绑定鼠标滚轮
        def on_mousewheel(event):
          canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
        canvas.bind("<MouseWheel>", on_mousewheel)
    
        # 主标题
        title_frame = ttk.Frame(self.inner_frame, style="Title.TLabel")
        title_frame.pack(fill="x", padx=20, pady=10)
    
        title = ttk.Label(title_frame, text=self.t("title"), style="Title.TLabel")
        title.pack()
    
        # 主内容区域 - 使用PanedWindow实现可调整的分割
        main_paned = ttk.PanedWindow(self.inner_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True, padx=20, pady=10)
    
        # 左侧区域 - 文件操作和预览 (2/3宽度)
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=2)
    
        # 右侧区域 - 功能选项 (1/3宽度)
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
    
        # 设置左侧区域
        self.setup_left_panel(left_frame)
    
        # 设置右侧区域
        self.setup_right_panel(right_frame)
    
    def setup_left_panel(self, parent):
        """设置左侧面板 - 文件操作和预览"""
        # 文件选择区域
        self.file_operations_frame = ttk.LabelFrame(parent, text=self.t("file_operations"), padding=15, style="Section.TLabelframe")
        self.file_operations_frame.pack(fill="x", padx=5, pady=5)
        
        # 输入文件
        input_frame = ttk.Frame(self.file_operations_frame)
        input_frame.pack(fill="x", pady=10)
        
        self.source_file_label = ttk.Label(input_frame, text=self.t("source_file"), font=("Arial", 10, "bold"))
        self.source_file_label.pack(anchor="w")
        
        input_entry_frame = ttk.Frame(input_frame)
        input_entry_frame.pack(fill="x", pady=5)
        
        ttk.Entry(input_entry_frame, textvariable=self.input_file, width=50, font=("Arial", 9)).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.input_browse_button = ttk.Button(input_entry_frame, text=self.t("browse"), command=self.browse_input_file, style="Action.TButton")
        self.input_browse_button.pack(side="right")
        
        # 输出文件
        output_frame = ttk.Frame(self.file_operations_frame)
        output_frame.pack(fill="x", pady=10)
        
        self.output_file_label = ttk.Label(output_frame, text=self.t("output_file"), font=("Arial", 10, "bold"))
        self.output_file_label.pack(anchor="w")
        
        output_entry_frame = ttk.Frame(output_frame)
        output_entry_frame.pack(fill="x", pady=5)
        
        ttk.Entry(output_entry_frame, textvariable=self.output_file, width=50, font=("Arial", 9)).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.output_browse_button = ttk.Button(output_entry_frame, text=self.t("browse"), command=self.browse_output_file, style="Action.TButton")
        self.output_browse_button.pack(side="right")
        
        # 文件信息预览
        self.file_info_frame = ttk.LabelFrame(parent, text=self.t("file_info"), padding=15, style="Section.TLabelframe")
        self.file_info_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.file_info = scrolledtext.ScrolledText(self.file_info_frame, wrap="word", height=8, font=("Arial", 9))
        self.file_info.pack(fill="both", expand=True)
        self.file_info.config(state="disabled")
        
        # 进度显示区域
        self.progress_frame = ttk.LabelFrame(parent, text=self.t("progress"), padding=15, style="Section.TLabelframe")
        self.progress_frame.pack(fill="x", padx=5, pady=5)
    
        # 添加进度标签
        self.progress_label = ttk.Label(
          self.progress_frame,
          text=self.t("progress"),
          font=("Arial", 10, "bold")
        )
        self.progress_label.pack(anchor="w", pady=(0, 10))
    
        # 进度条
        self.determinate_progress = ttk.Progressbar(
        self.progress_frame, 
        mode='determinate',
        variable=self.progress_var,
        length=400
        )
        self.determinate_progress.pack(fill="x", pady=5)

        # 进度百分比
        progress_info_frame = ttk.Frame(self.progress_frame)
        progress_info_frame.pack(fill="x", pady=5)
        
        self.progress_percent_label = ttk.Label(
            progress_info_frame, 
            textvariable=self.progress_percent,
            font=("Arial", 10, "bold")
        )
        self.progress_percent_label.pack(side="left")
        
        self.estimated_time_label = ttk.Label(
            progress_info_frame, 
            text=self.t("estimated_time") + ": --:--",
            font=("Arial", 9)
        )
        self.estimated_time_label.pack(side="right")
        
        # 当前处理文件
        self.processing_file_label = ttk.Label(
            self.progress_frame, 
            text=self.t("processing_file") + ": ",
            font=("Arial", 9)
        )
        self.processing_file_label.pack(anchor="w")
        
        # 等待完成信息
        self.waiting_label = ttk.Label(
            self.progress_frame,
            text="",
            font=("Arial", 9, "italic"),
            foreground="blue"
        )
        self.waiting_label.pack(anchor="w", pady=(5, 0))
        
        # 命令预览和执行
        self.command_preview_frame = ttk.LabelFrame(parent, text=self.t("command_preview"), padding=15, style="Section.TLabelframe")
        self.command_preview_frame.pack(fill="x", padx=5, pady=5)
        
        self.command_preview = scrolledtext.ScrolledText(self.command_preview_frame, wrap="word", height=4, font=("Consolas", 9))
        self.command_preview.pack(fill="x", pady=5)
        
        action_frame = ttk.Frame(self.command_preview_frame)
        action_frame.pack(fill="x", pady=5)
        
        self.update_preview_button = ttk.Button(action_frame, text=self.t("update_preview"), command=self.update_preview, style="Action.TButton")
        self.update_preview_button.pack(side="left", padx=(0, 10))
        self.process_btn = ttk.Button(action_frame, text=self.t("start_processing"), command=self.start_processing, style="Primary.TButton")
        self.process_btn.pack(side="left")
        
        # 状态显示
        self.status_label = ttk.Label(self.command_preview_frame, text=self.t("ready"), font=("Arial", 9))
        self.status_label.pack(anchor="w")
    
    def setup_right_panel(self, parent):
        """设置右侧面板 - 功能选项"""
        # 创建笔记本样式实现分类
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 基础操作标签页
        basic_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(basic_frame, text="🔄 " + self.t("format_conversion").replace("🔄 ", ""))
        
        # 视频处理标签页
        video_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(video_frame, text="🎬 " + self.t("video_encoding").replace("🎬 ", ""))
        
        # 音频处理标签页
        audio_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(audio_frame, text="🎵 " + self.t("audio_settings").replace("🎵 ", ""))
        
        # 高级功能标签页
        advanced_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(advanced_frame, text="🔧 " + self.t("custom_parameters").replace("🔧 ", ""))
        
        # 设置标签页
        settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(settings_frame, text="⚙️ " + self.t("settings").replace("⚙️ ", ""))
        
        # 设置各标签页内容
        self.setup_basic_tab(basic_frame)
        self.setup_video_tab(video_frame)
        self.setup_audio_tab(audio_frame)
        self.setup_advanced_tab(advanced_frame)
        self.setup_settings_tab(settings_frame)
    
    def setup_basic_tab(self, parent):
        """设置基础操作标签页"""
        # 格式转换
        self.convert_frame = ttk.LabelFrame(parent, text=self.t("format_conversion"), padding=10, style="Section.TLabelframe")
        self.convert_frame.pack(fill="x", pady=5)
        
        self.output_format_label = ttk.Label(self.convert_frame, text=self.t("output_format"))
        self.output_format_label.grid(row=0, column=0, sticky="w", pady=5)
        self.format_var = tk.StringVar(value="mp4")
        
        # 添加ncm_to_mp3选项
        formats = ["mp4", "avi", "mov", "mkv", "webm", "mp3", "wav", "flac", "aac", "m4a", "ncm_to_mp3"]
        format_combo = ttk.Combobox(self.convert_frame, textvariable=self.format_var, values=formats, width=15, state="readonly")
        format_combo.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        
        self.convert_button = ttk.Button(self.convert_frame, text=self.t("convert_format"), command=self.convert_format, style="Action.TButton")
        self.convert_button.grid(row=0, column=2, padx=10, pady=5)
        
        # 添加NCM转换说明标签
        self.ncm_info_label = ttk.Label(
            self.convert_frame, 
            text="🎵 NCM转MP3: 需要先解密NCM文件", 
            font=("Arial", 8),
            foreground="blue"
        )
        self.ncm_info_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=2)
        
        # 质量设置
        self.quality_frame = ttk.LabelFrame(parent, text=self.t("quality_settings"), padding=10, style="Section.TLabelframe")
        self.quality_frame.pack(fill="x", pady=5)
        self.quality_frame = ttk.LabelFrame(parent, text=self.t("quality_settings"), padding=10, style="Section.TLabelframe")

        self.video_quality_label = ttk.Label(self.quality_frame, text=self.t("video_quality"))
        self.video_quality_label.grid(row=0, column=0, sticky="w", pady=3)
        self.video_quality = tk.StringVar(value=self.t("medium_quality"))
        qualities = [self.t("high_quality"), self.t("medium_quality"), self.t("low_quality"), self.t("original_quality")]
        self.video_quality_combo = ttk.Combobox(self.quality_frame, textvariable=self.video_quality, values=qualities, width=12, state="readonly")
        self.video_quality_combo.grid(row=0, column=1, sticky="w", pady=3, padx=5)
        
        self.audio_quality_label = ttk.Label(self.quality_frame, text=self.t("audio_quality"))
        self.audio_quality_label.grid(row=1, column=0, sticky="w", pady=3)
        self.audio_quality = tk.StringVar(value=self.t("medium_quality"))
        self.audio_quality_combo = ttk.Combobox(self.quality_frame, textvariable=self.audio_quality, values=qualities, width=12, state="readonly")
        self.audio_quality_combo.grid(row=1, column=1, sticky="w", pady=3, padx=5)
        
        # 快速操作
        self.quick_frame = ttk.LabelFrame(parent, text=self.t("quick_actions"), padding=10, style="Section.TLabelframe")
        self.quick_frame.pack(fill="x", pady=5)
        self.quick_frame = ttk.LabelFrame(parent, text=self.t("quick_actions"), padding=10, style="Section.TLabelframe")
        self.quick_frame.pack(fill="x", pady=5)

        self.extract_audio_button = ttk.Button(self.quick_frame, text=self.t("extract_audio"), command=self.extract_audio, style="Action.TButton")
        self.extract_audio_button.pack(fill="x", pady=3)
        self.ncm_to_mp3_button = ttk.Button(
            self.quick_frame, 
            text="🎵 NCM转MP3", 
            command=self.quick_ncm_to_mp3, 
            style="Action.TButton"
        )
        self.ncm_to_mp3_button.pack(fill="x", pady=3)

        self.extract_audio_button = ttk.Button(self.quick_frame, text=self.t("extract_audio"), command=self.extract_audio, style="Action.TButton")
        self.extract_audio_button.pack(fill="x", pady=3)
        self.extract_video_button = ttk.Button(self.quick_frame, text=self.t("extract_video"), command=self.extract_video, style="Action.TButton")
        self.extract_video_button.pack(fill="x", pady=3)
        
        self.compress_media_button = ttk.Button(self.quick_frame, text=self.t("compress_media"), command=self.compress_media, style="Action.TButton")
        self.compress_media_button.pack(fill="x", pady=3)
    
    def setup_video_tab(self, parent):
        """设置视频处理标签页"""
        # 视频编码设置
        self.video_encoding_frame = ttk.LabelFrame(parent, text=self.t("video_encoding"), padding=10, style="Section.TLabelframe")
        self.video_encoding_frame.pack(fill="x", pady=5)
        
        self.video_encoder_label = ttk.Label(self.video_encoding_frame, text=self.t("video_encoder"))
        self.video_encoder_label.grid(row=0, column=0, sticky="w", pady=3)
        self.video_codec = tk.StringVar(value="libx264")
        
        # 根据硬件加速支持动态生成编码器选项
        codecs = ["libx264", "libx265", "mpeg4", "vp9", "copy"]
        
        # 添加硬件加速编码器（如果支持）
        for encoder, info in self.hardware_encoders.items():
            if info["supported"]:
                codecs.append(encoder)
            
        # 创建编码器选择框
        self.video_codec_combo = ttk.Combobox(self.video_encoding_frame, textvariable=self.video_codec, values=codecs, width=15, state="readonly")
        self.video_codec_combo.grid(row=0, column=1, sticky="w", pady=3, padx=5)
        
        self.resolution_label = ttk.Label(self.video_encoding_frame, text=self.t("resolution"))
        self.resolution_label.grid(row=1, column=0, sticky="w", pady=3)
        self.resolution = tk.StringVar(value=self.t("original_resolution"))
        resolutions = [self.t("original_resolution"), "3840x2160", "1920x1080", "1280x720", "854x480", "640x360"]
        self.resolution_combo = ttk.Combobox(self.video_encoding_frame, textvariable=self.resolution, values=resolutions, width=15, state="readonly")
        self.resolution_combo.grid(row=1, column=1, sticky="w", pady=3, padx=5)
        
        self.fps_label = ttk.Label(self.video_encoding_frame, text=self.t("fps"))
        self.fps_label.grid(row=2, column=0, sticky="w", pady=3)
        self.fps = tk.StringVar(value=self.t("original_fps"))
        fps_values = [self.t("original_fps"), "60", "30", "25", "24", "15"]
        self.fps_combo = ttk.Combobox(self.video_encoding_frame, textvariable=self.fps, values=fps_values, width=15, state="readonly")
        self.fps_combo.grid(row=2, column=1, sticky="w", pady=3, padx=5)
        
        # 硬件加速选项
        hwaccel_frame = ttk.LabelFrame(parent, text=self.t("hardware_acceleration"), padding=10, style="Section.TLabelframe")
        hwaccel_frame.pack(fill="x", pady=5)
        
        self.hwaccel_var = tk.StringVar(value=self.t("hwaccel_none"))
        hwaccel_options = [self.t("hwaccel_none")]
        
        # 只添加支持的硬件加速选项
        for hwaccel, info in self.hardware_acceleration.items():
            if info["supported"]:
                hwaccel_options.append(info["name"])
        
        hwaccel_combo = ttk.Combobox(hwaccel_frame, textvariable=self.hwaccel_var, values=hwaccel_options, width=20, state="readonly")
        hwaccel_combo.pack(fill="x", pady=5)
        
        # 视频滤镜
        self.video_filters_frame = ttk.LabelFrame(parent, text=self.t("video_filters"), padding=10, style="Section.TLabelframe")
        self.video_filters_frame.pack(fill="x", pady=5)
        
        self.enable_crop = tk.BooleanVar()
        self.crop_video_check = ttk.Checkbutton(self.video_filters_frame, text=self.t("crop_video"), variable=self.enable_crop)
        self.crop_video_check.grid(row=0, column=0, sticky="w", pady=3)
        
        self.crop_params_label = ttk.Label(self.video_filters_frame, text=self.t("crop_params"))
        self.crop_params_label.grid(row=0, column=1, sticky="w", pady=3)
        self.crop_params = tk.StringVar(value="iw:ih:0:0")
        ttk.Entry(self.video_filters_frame, textvariable=self.crop_params, width=15).grid(row=0, column=2, pady=3, padx=5)
        
        self.enable_scale = tk.BooleanVar()
        self.scale_video_check = ttk.Checkbutton(self.video_filters_frame, text=self.t("scale_video"), variable=self.enable_scale)
        self.scale_video_check.grid(row=1, column=0, sticky="w", pady=3)
        
        self.enable_rotate = tk.BooleanVar()
        self.rotate_video_check = ttk.Checkbutton(self.video_filters_frame, text=self.t("rotate_video"), variable=self.enable_rotate)
        self.rotate_video_check.grid(row=2, column=0, sticky="w", pady=3)
        
        self.rotate_angle_label = ttk.Label(self.video_filters_frame, text=self.t("rotate_angle"))
        self.rotate_angle_label.grid(row=2, column=1, sticky="w", pady=3)
        self.rotate_angle = tk.StringVar(value="90")
        angles = ["90", "180", "270"]
        ttk.Combobox(self.video_filters_frame, textvariable=self.rotate_angle, values=angles, width=8, state="readonly").grid(row=2, column=2, pady=3, padx=5)
        
        self.apply_video_processing_button = ttk.Button(parent, text=self.t("apply_video_processing"), command=self.apply_video_processing, style="Action.TButton")
        self.apply_video_processing_button.pack(fill="x", pady=10)
    
    def setup_audio_tab(self, parent):
        """设置音频处理标签页"""
        self.audio_settings_frame = ttk.LabelFrame(parent, text=self.t("audio_settings"), padding=10, style="Section.TLabelframe")
        self.audio_settings_frame.pack(fill="x", pady=5)
        
        self.audio_encoder_label = ttk.Label(self.audio_settings_frame, text=self.t("audio_encoder"))
        self.audio_encoder_label.grid(row=0, column=0, sticky="w", pady=3)
        self.audio_codec = tk.StringVar(value="aac")
        audio_codecs = ["aac", "mp3", "flac", "opus", "copy", "libmp3lame"]
        ttk.Combobox(self.audio_settings_frame, textvariable=self.audio_codec, values=audio_codecs, width=15, state="readonly").grid(row=0, column=1, sticky="w", pady=3, padx=5)
        
        self.sample_rate_label = ttk.Label(self.audio_settings_frame, text=self.t("sample_rate"))
        self.sample_rate_label.grid(row=1, column=0, sticky="w", pady=3)
        self.sample_rate = tk.StringVar(value="44100")
        sample_rates = ["44100", "48000", "22050", "16000"]
        ttk.Combobox(self.audio_settings_frame, textvariable=self.sample_rate, values=sample_rates, width=15, state="readonly").grid(row=1, column=1, sticky="w", pady=3, padx=5)
        
        self.channels_label = ttk.Label(self.audio_settings_frame, text=self.t("channels"))
        self.channels_label.grid(row=2, column=0, sticky="w", pady=3)
        self.channels = tk.StringVar(value="2")
        channels = ["1", "2", self.t("original_quality").replace("质量", "声道")]
        self.channels_combo = ttk.Combobox(self.audio_settings_frame, textvariable=self.channels, values=channels, width=15, state="readonly")
        self.channels_combo.grid(row=2, column=1, sticky="w", pady=3, padx=5)
        
        self.bitrate_label = ttk.Label(self.audio_settings_frame, text=self.t("bitrate"))
        self.bitrate_label.grid(row=3, column=0, sticky="w", pady=3)
        self.audio_bitrate = tk.StringVar(value="128k")
        bitrates = ["64k", "128k", "192k", "256k", "320k"]
        ttk.Combobox(self.audio_settings_frame, textvariable=self.audio_bitrate, values=bitrates, width=15, state="readonly").grid(row=3, column=1, sticky="w", pady=3, padx=5)
        
        # 音频滤镜
        self.audio_filters_frame = ttk.LabelFrame(parent, text=self.t("audio_filters"), padding=10, style="Section.TLabelframe")
        self.audio_filters_frame.pack(fill="x", pady=5)
        
        self.enable_volume = tk.BooleanVar()
        self.adjust_volume_check = ttk.Checkbutton(self.audio_filters_frame, text=self.t("adjust_volume"), variable=self.enable_volume)
        self.adjust_volume_check.grid(row=0, column=0, sticky="w", pady=3)
        
        self.volume_factor_label = ttk.Label(self.audio_filters_frame, text=self.t("volume_factor"))
        self.volume_factor_label.grid(row=0, column=1, sticky="w", pady=3)
        self.volume_factor = tk.StringVar(value="1.0")
        ttk.Entry(self.audio_filters_frame, textvariable=self.volume_factor, width=10).grid(row=0, column=2, pady=3, padx=5)
        
        self.apply_audio_processing_button = ttk.Button(parent, text=self.t("apply_audio_processing"), command=self.apply_audio_processing, style="Action.TButton")
        self.apply_audio_processing_button.pack(fill="x", pady=10)
    
    def setup_advanced_tab(self, parent):
        """设置高级功能标签页"""
        # 自定义参数
        self.custom_parameters_frame = ttk.LabelFrame(parent, text=self.t("custom_parameters"), padding=10, style="Section.TLabelframe")
        self.custom_parameters_frame.pack(fill="x", pady=5)
        
        self.ffmpeg_parameters_label = ttk.Label(self.custom_parameters_frame, text=self.t("ffmpeg_parameters"))
        self.ffmpeg_parameters_label.pack(anchor="w", pady=5)
        self.custom_args = tk.StringVar()
        custom_entry = ttk.Entry(self.custom_parameters_frame, textvariable=self.custom_args, width=50)
        custom_entry.pack(fill="x", pady=5)
        
        self.example_label = ttk.Label(self.custom_parameters_frame, text=self.t("example"), font=("Arial", 8))
        self.example_label.pack(anchor="w")
        
        self.run_custom_command_button = ttk.Button(self.custom_parameters_frame, text=self.t("run_custom_command"), command=self.run_custom_command, style="Action.TButton")
        self.run_custom_command_button.pack(anchor="w", pady=10)
        
        # 预设配置
        self.preset_configs_frame = ttk.LabelFrame(parent, text=self.t("preset_configs"), padding=10, style="Section.TLabelframe")
        self.preset_configs_frame.pack(fill="x", pady=5)
        
        self.preset_var = tk.StringVar(value=self.t("no_preset"))
        presets = [self.t("no_preset"), self.t("high_quality_mp4"), self.t("high_quality_mp3"), 
                  self.t("web_optimized"), self.t("mobile_optimized")]
        self.preset_combo = ttk.Combobox(self.preset_configs_frame, textvariable=self.preset_var, values=presets, width=20, state="readonly")
        self.preset_combo.pack(fill="x", pady=5)
        self.preset_combo.bind('<<ComboboxSelected>>', self.apply_preset)
    
    def setup_settings_tab(self, parent):
        """设置设置标签页"""
        # 语言设置
        self.language_frame = ttk.LabelFrame(parent, text=self.t("language_settings"), padding=10, style="Section.TLabelframe")
        self.language_frame.pack(fill="x", pady=5)
        
        language_buttons_frame = ttk.Frame(self.language_frame)
        language_buttons_frame.pack(fill="x", pady=5)
        
        self.switch_to_english_button = ttk.Button(
            language_buttons_frame, 
            text=self.t("switch_to_english"), 
            command=lambda: self.switch_language("en_US"),
            style="Action.TButton"
        )
        self.switch_to_english_button.pack(side="left", padx=(0, 10))
        
        self.switch_to_chinese_button = ttk.Button(
            language_buttons_frame, 
            text=self.t("switch_to_chinese"), 
            command=lambda: self.switch_language("zh_CN"),
            style="Action.TButton"
        )
        self.switch_to_chinese_button.pack(side="left")
        
        # 硬件加速设置
        self.hardware_accel_frame = ttk.LabelFrame(parent, text=self.t("hardware_accel_settings"), padding=10, style="Section.TLabelframe")
        self.hardware_accel_frame.pack(fill="x", pady=5)
        
        self.hardware_detection_label = ttk.Label(self.hardware_accel_frame, text=self.t("hardware_detection"), font=("Arial", 10, "bold"))
        self.hardware_detection_label.pack(anchor="w", pady=5)
        
        # 显示硬件加速状态
        self.hardware_status_label = ttk.Label(self.hardware_accel_frame, text=self.t("hardware_status"), font=("Arial", 9))
        self.hardware_status_label.pack(anchor="w", pady=2)
        
        # 显示检测到的硬件加速支持
        hardware_status_text = ""
        supported_count = 0
        
        for hwaccel, info in self.hardware_acceleration.items():
            if info["supported"]:
                hardware_status_text += f"✅ {info['name']}\n"
                supported_count += 1
        
        if supported_count == 0:
            hardware_status_text = self.t("no_hardware_support")
        else:
            hardware_status_text = self.t("hardware_support_detected") + f" ({supported_count}):\n" + hardware_status_text
        
        hardware_status_display = ttk.Label(self.hardware_accel_frame, text=hardware_status_text, font=("Arial", 9))
        hardware_status_display.pack(anchor="w", pady=5)
        
        # 显示硬件编码器状态
        self.hardware_encoders_label = ttk.Label(self.hardware_accel_frame, text=self.t("hardware_encoders"), font=("Arial", 9))
        self.hardware_encoders_label.pack(anchor="w", pady=2)
        
        # 显示检测到的硬件编码器支持
        hardware_encoders_text = ""
        encoder_supported_count = 0
        
        for encoder, info in self.hardware_encoders.items():
            if info["supported"]:
                hardware_encoders_text += f"✅ {info['name']}\n"
                encoder_supported_count += 1
        
        if encoder_supported_count == 0:
            hardware_encoders_text = self.t("no_hardware_support")
        else:
            hardware_encoders_text = self.t("hardware_support_detected") + f" ({encoder_supported_count}):\n" + hardware_encoders_text
        
        hardware_encoders_display = ttk.Label(self.hardware_accel_frame, text=hardware_encoders_text, font=("Arial", 9))
        hardware_encoders_display.pack(anchor="w", pady=5)
        
        # 重新检测按钮
        self.detect_hardware_button = ttk.Button(
            self.hardware_accel_frame, 
            text=self.t("re_detect"), 
            command=self.redetect_hardware_acceleration,
            style="Action.TButton"
        )
        self.detect_hardware_button.pack(anchor="w", pady=10)
        
        # 版本信息
        self.version_frame = ttk.LabelFrame(parent, text=self.t("version_info"), padding=10, style="Section.TLabelframe")
        self.version_frame.pack(fill="x", pady=5)
        
        self.current_version_label = ttk.Label(self.version_frame, text=self.t("current_version") + " " + self.version, font=("Arial", 10))
        self.current_version_label.pack(anchor="w", pady=5)
    
    def redetect_hardware_acceleration(self):
        """重新检测硬件加速"""
        # 显示进度条
        self.progress_var.set(0)
        self.progress_percent.set("0%")
        self.determinate_progress.start()
        
        # 在后台线程中检测
        def detect():
            self.detect_hardware_acceleration()
            self.detect_hardware_encoders()
            self.root.after(0, self.on_detection_complete)
        
        threading.Thread(target=detect, daemon=True).start()
    
    def on_detection_complete(self):
        """硬件检测完成"""
        self.determinate_progress.stop()
        self.progress_var.set(100)
        self.progress_percent.set("100%")
        messagebox.showinfo(self.t("detection_completed"), self.t("hardware_support_detected"))
        # 刷新设置界面和视频编码器选项
        self.refresh_settings_tab()
        self.refresh_video_encoder_options()
    
    def refresh_settings_tab(self):
        """刷新设置标签页 - 简化稳定版"""
        try:
            # 查找设置标签页
            settings_tab_index = None
            for i in range(self.notebook.index("end")):
                tab_text = self.notebook.tab(i, "text")
                if "设置" in tab_text or "Settings" in tab_text or "⚙️" in tab_text:
                    settings_tab_index = i
                    break
        
            if settings_tab_index is not None:
                # 获取设置标签页的frame
                settings_frame = self.notebook.winfo_children()[settings_tab_index]
            
                # 清除原有内容
                for widget in settings_frame.winfo_children():
                    widget.destroy()
            
                # 重新设置内容
                self.setup_settings_tab(settings_frame)
            
        except Exception as e:
            print(f"刷新设置标签页时出错: {e}")
            # 在状态栏显示错误信息
            self.status_label.config(text=f"刷新设置失败: {str(e)}")

    def refresh_video_encoder_options(self):
        """刷新视频编码器选项"""
        # 根据硬件加速支持动态生成编码器选项
        codecs = ["libx264", "libx265", "mpeg4", "vp9", "copy"]
        
        # 添加硬件加速编码器（如果支持）
        for encoder, info in self.hardware_encoders.items():
            if info["supported"]:
                codecs.append(encoder)
        
        # 更新编码器选择框的值
        self.video_codec_combo.configure(values=codecs)
        
        # 如果当前选择的编码器不再支持，则重置为默认值
        current_value = self.video_codec.get()
        if current_value not in codecs:
            self.video_codec.set("libx264")

    def convert_ncm_to_mp3(self):
        """NCM转MP3专用方法"""
        try:
            input_file = self.input_file.get()
            output_file = self.output_file.get()
        
            # 更新状态
            self.status_label.config(text="🔓 正在解密NCM文件...")
            self.progress_var.set(10)
            self.progress_percent.set("10%")
            self.root.update()
        
            # 解密NCM文件
            try:
                # 尝试使用ncmdump库
                from ncmdump import dump
                decrypted_file = dump(input_file)
            except ImportError:
                # 如果ncmdump不可用，使用内置解密
                self.status_label.config(text="🔓 使用内置解密方法...")
                decrypted_file = self.decrypt_ncm_fallback(input_file)
            except Exception as e:
                raise Exception(f"NCM解密失败: {str(e)}")
        
            # 更新进度
            self.progress_var.set(50)
            self.progress_percent.set("50%")
            self.status_label.config(text="🔄 正在转换格式...")
            self.root.update()
        
            # 如果解密后的文件不是MP3，使用FFmpeg转换
            if not decrypted_file.lower().endswith('.mp3'):
                cmd = [
                    "ffmpeg", "-i", decrypted_file, 
                    "-codec:a", "libmp3lame", 
                    "-q:a", "2",  # 高质量VBR
                    "-y", output_file
                ]
            
                # 运行FFmpeg转换
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
                # 删除临时文件
                try:
                    os.remove(decrypted_file)
                except:
                    pass
            else:
                 # 如果已经是MP3，直接重命名
                import shutil
                shutil.move(decrypted_file, output_file)
        
            # 完成
            self.progress_var.set(100)
            self.progress_percent.set("100%")
            self.status_label.config(text="✅ NCM转MP3完成！")
            messagebox.showinfo("完成", f"NCM文件已成功转换为MP3:\n{output_file}")
        
        except subprocess.CalledProcessError as e:
            self.status_label.config(text="❌ 转换失败")
            messagebox.showerror("错误", f"FFmpeg转换失败:\n{e.stderr}")
        except Exception as e:
            self.status_label.config(text="❌ 转换失败")
            messagebox.showerror("错误", f"NCM转MP3失败:\n{str(e)}")
    
        finally:
            # 重置按钮状态
            self.process_btn.config(text=self.t("start_processing"))
            self.is_processing = False

    def decrypt_ncm_file(self, ncm_file_path):
        """解密NCM文件"""
        try:
            # 导入ncmdump模块
            try:
                from ncmdump import dump
            except ImportError:
                # 如果ncmdump不可用，尝试使用其他方法
                return self.decrypt_ncm_fallback(ncm_file_path)
            
            # 使用ncmdump解密
            output_file = dump(ncm_file_path)
            return output_file
            
        except Exception as e:
            print(f"NCM解密失败: {e}")
            return self.decrypt_ncm_fallback(ncm_file_path)

    def decrypt_ncm_fallback(self, ncm_file_path):
        """备用NCM解密方法"""
        try:
            import struct
            import hashlib
            from Crypto.Cipher import AES
            import base64
        
            with open(ncm_file_path, 'rb') as f:
                data = f.read()
        
            # 检查NCM文件格式
            if len(data) < 10 or data[:10] != b'CTENFDAM\x00\x00':
                raise ValueError("不是有效的NCM文件")
        
            # NCM文件结构解析
            offset = 10
        
            # 读取密钥长度
            if len(data) < offset + 4:
                raise ValueError("文件格式错误")
            key_length = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
        
            # 读取密钥数据
            if len(data) < offset + key_length:
                raise ValueError("密钥数据不完整")
            key_data = data[offset:offset+key_length]
            offset += key_length
        
             # 读取元数据长度
            if len(data) < offset + 4:
                raise ValueError("元数据长度错误")
            meta_length = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
        
            # 跳过元数据
            if len(data) < offset + meta_length:
                raise ValueError("元数据不完整")
            offset += meta_length
        
            # 跳过封面图像数据（如果有）
            if len(data) < offset + 4:
                raise ValueError("封面数据长度错误")
            image_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
        
            if image_size > 0:
                if len(data) < offset + image_size:
                    raise ValueError("封面数据不完整")
                offset += image_size
        
            # 剩余的是加密的音乐数据
            encrypted_data = data[offset:]
        
            if not encrypted_data:
                raise ValueError("没有找到加密的音乐数据")
        
            # 使用简单的XOR解密（这是简化版本）
            core_key = b'hzHRAmso5kInbaxW'
            key = hashlib.md5(core_key).digest()
        
            # 解密数据
            decrypted_data = bytearray()
            for i in range(len(encrypted_data)):
                decrypted_data.append(encrypted_data[i] ^ key[i % len(key)])
        
            # 保存为临时MP3文件
            import tempfile
            import uuid
        
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            temp_filename = f"ncm_decrypted_{uuid.uuid4().hex}.mp3"
            temp_file_path = os.path.join(temp_dir, temp_filename)
        
            with open(temp_file_path, 'wb') as f:
                f.write(decrypted_data)
        
            return temp_file_path
        
        except Exception as e:
            print(f"备用解密方法失败: {e}")
            # 如果内置解密也失败，提供更友好的错误信息
            error_msg = f"NCM文件解密失败:\n{str(e)}\n\n请确保：\n1. 文件是有效的NCM格式\n2. 文件没有被损坏\n3. 尝试使用在线转换工具"
            raise Exception(error_msg)
        
    def quick_ncm_to_mp3(self):
        """快速NCM转MP3"""
        if not self.input_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_file"))
            return
    
        input_file = self.input_file.get()
        if not input_file.lower().endswith('.ncm'):
            messagebox.showwarning("警告", "请选择.ncm文件")
            return
    
        # 设置输出文件
        base, _ = os.path.splitext(input_file)
        output_file = base + ".mp3"
        self.output_file.set(output_file)
     
        # 设置格式为ncm_to_mp3
        self.format_var.set("ncm_to_mp3")
    
        # 开始转换
        self.convert_ncm_to_mp3()  
         
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title=self.t("source_file"),
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv *.m4v"),
                ("音频文件", "*.mp3 *.wav *.flac *.aac *.m4a *.ogg *.wma *.ncm"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            # 自动生成输出文件名
            if not self.output_file.get():
                base, ext = os.path.splitext(filename)
                output_ext = "." + self.format_var.get() if hasattr(self, 'format_var') else ext
                self.output_file.set(f"{base}_converted{output_ext}")
            
            # 获取文件信息
            self.get_file_info(filename)
    
    def browse_output_file(self):
        """浏览输出文件位置"""
        default_ext = "." + self.format_var.get() if hasattr(self, 'format_var') else ".mp4"
        filename = filedialog.asksaveasfilename(
            title=self.t("output_file"),
            defaultextension=default_ext,
            filetypes=[
                ("MP4文件", "*.mp4"),
                ("AVI文件", "*.avi"), 
                ("MOV文件", "*.mov"),
                ("MKV文件", "*.mkv"),
                ("MP3文件", "*.mp3"),
                ("WAV文件", "*.wav"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            # 自动生成输出文件名
            if not self.output_file.get():
                base, ext = os.path.splitext(filename)
                # 如果是NCM文件，默认输出为MP3
                if ext.lower() == '.ncm':
                    output_ext = ".mp3"
            else:
                output_ext = "." + self.format_var.get() if hasattr(self, 'format_var') else ext
            self.output_file.set(f"{base}_converted{output_ext}")
            
            # 获取文件信息
            self.output_file.set(filename)
    
    def get_file_info(self, filename):
        """获取媒体文件信息"""
        try:
            # 如果是NCM文件，显示特殊信息
            if filename.lower().endswith('.ncm'):
                self.file_info.config(state="normal")
                self.file_info.delete(1.0, tk.END)
                self.file_info.insert(1.0, "🎵 NCM加密音频文件\n")
                self.file_info.insert(tk.END, f"📄 文件: {os.path.basename(filename)}\n")
                self.file_info.insert(tk.END, f"📁 路径: {filename}\n")
                try:
                    size_mb = os.path.getsize(filename) / (1024 * 1024)
                    self.file_info.insert(tk.END, f"💾 大小: {size_mb:.2f} MB\n")
                except Exception:
                    self.file_info.insert(tk.END, "💾 大小: 无法读取\n")
                self.file_info.insert(tk.END, "🔓 状态: 加密文件，需要解密\n")
                self.file_info.insert(tk.END, f"🔄 支持: {'ncmdump' if getattr(self, 'ncmdump_available', False) else '内置解密'}\n")
                self.file_info.config(state="disabled")
                return

            # 其他文件类型使用 ffprobe 获取信息
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filename],
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                errors='ignore'
            )

            info = json.loads(result.stdout or "{}")

            self.file_info.config(state="normal")
            self.file_info.delete(1.0, tk.END)

            # 显示基本信息
            self.file_info.insert(1.0, f"📄 文件: {os.path.basename(filename)}\n")
            self.file_info.insert(tk.END, f"📁 路径: {filename}\n")
            try:
                size_mb = os.path.getsize(filename) / (1024 * 1024)
                self.file_info.insert(tk.END, f"💾 大小: {size_mb:.2f} MB\n")
            except Exception:
                self.file_info.insert(tk.END, "💾 大小: 无法读取\n")

            # 显示格式信息
            if 'format' in info and info['format']:
                format_info = info['format']
                self.file_info.insert(tk.END, f"📋 格式: {format_info.get('format_name', '未知')}\n")
                duration = float(format_info.get('duration', 0) or 0)
                self.file_info.insert(tk.END, f"⏱️ 时长: {duration:.2f} 秒\n")
                try:
                    bit_rate = int(format_info.get('bit_rate', 0) or 0)
                    self.file_info.insert(tk.END, f"📊 比特率: {bit_rate / 1000:.0f} kbps\n")
                except Exception:
                    pass

            # 显示流信息
            if 'streams' in info and info['streams']:
                video_streams = [s for s in info['streams'] if s.get('codec_type') == 'video']
                audio_streams = [s for s in info['streams'] if s.get('codec_type') == 'audio']

                if video_streams:
                    video = video_streams[0]
                    self.file_info.insert(tk.END, f"🎥 视频: {video.get('codec_name', '未知')}\n")
                    width = video.get('width', '未知')
                    height = video.get('height', '未知')
                    self.file_info.insert(tk.END, f"📐 分辨率: {width}x{height}\n")
                    self.file_info.insert(tk.END, f"🎞️ 帧率: {video.get('r_frame_rate', '未知')}\n")

                if audio_streams:
                    audio = audio_streams[0]
                    self.file_info.insert(tk.END, f"🎵 音频: {audio.get('codec_name', '未知')}\n")
                    self.file_info.insert(tk.END, f"🔊 声道: {audio.get('channels', '未知')}\n")
                    self.file_info.insert(tk.END, f"🎚️ 采样率: {audio.get('sample_rate', '未知')} Hz\n")

            self.file_info.config(state="disabled")

        except Exception as e:
            try:
                self.file_info.config(state="normal")
                self.file_info.delete(1.0, tk.END)
                self.file_info.insert(1.0, f"❌ 无法获取文件信息: {str(e)}")
                self.file_info.config(state="disabled")
            except Exception:
                # 如果连 UI 更新也失败，则打印日志到控制台以便调试
                print(f"无法显示文件信息错误: {e}")
    
    def build_ffmpeg_command(self):
        """构建FFmpeg命令"""
        if not self.input_file.get() or not self.output_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_output"))
            return None
        
        cmd = ["ffmpeg"]
        
        # 硬件加速设置 - 必须在输入文件之前
        hwaccel = self.hwaccel_var.get()
        if hwaccel != self.t("hwaccel_none"):
            # 根据选择的硬件加速器设置对应的参数
            if hwaccel == self.t("hwaccel_cuda"):
                cmd.extend(["-hwaccel", "cuda"])
            elif hwaccel == self.t("hwaccel_qsv"):
                cmd.extend(["-hwaccel", "qsv"])
            elif hwaccel == self.t("hwaccel_vaapi"):
                cmd.extend(["-hwaccel", "vaapi"])
            elif hwaccel == self.t("hwaccel_d3d11va"):
                cmd.extend(["-hwaccel", "d3d11va"])
            elif hwaccel == self.t("hwaccel_videotoolbox"):
                cmd.extend(["-hwaccel", "videotoolbox"])
            elif hwaccel == self.t("hwaccel_amf"):
                cmd.extend(["-hwaccel", "amf"])
        
        # 输入文件和覆盖选项
        cmd.extend(["-i", self.input_file.get(), "-y"])  # -y 覆盖输出文件
        
        # 视频编码参数
        if hasattr(self, 'video_codec') and self.video_codec.get() != "copy":
            cmd.extend(["-c:v", self.video_codec.get()])
        
        # 分辨率设置
        if hasattr(self, 'resolution') and self.resolution.get() != self.t("original_resolution"):
            cmd.extend(["-s", self.resolution.get()])
        
        # 帧率设置
        if hasattr(self, 'fps') and self.fps.get() != self.t("original_fps"):
            cmd.extend(["-r", self.fps.get()])
        
        # 音频编码参数
        if hasattr(self, 'audio_codec'):
            cmd.extend(["-c:a", self.audio_codec.get()])
        
        # 采样率
        if hasattr(self, 'sample_rate'):
            cmd.extend(["-ar", self.sample_rate.get()])
        
        # 声道数
        if hasattr(self, 'channels') and self.channels.get() != self.t("original_quality").replace("质量", "声道"):
            cmd.extend(["-ac", self.channels.get()])
        
        # 音频比特率
        if hasattr(self, 'audio_bitrate'):
            cmd.extend(["-b:a", self.audio_bitrate.get()])
        
        # 视频滤镜
        vf_filters = []
        if hasattr(self, 'enable_crop') and self.enable_crop.get():
            vf_filters.append(f"crop={self.crop_params.get()}")
        
        if hasattr(self, 'enable_scale') and self.enable_scale.get() and hasattr(self, 'resolution') and self.resolution.get() != self.t("original_resolution"):
            vf_filters.append(f"scale={self.resolution.get().replace('x', ':')}")
        
        if hasattr(self, 'enable_rotate') and self.enable_rotate.get():
            vf_filters.append(f"transpose={self.rotate_angle.get()}")
        
        if vf_filters:
            cmd.extend(["-vf", ",".join(vf_filters)])
        
        # 音频滤镜
        af_filters = []
        if hasattr(self, 'enable_volume') and self.enable_volume.get():
            af_filters.append(f"volume={self.volume_factor.get()}")
        
        if af_filters:
            cmd.extend(["-af", ",".join(af_filters)])
        
        # 质量设置
        if hasattr(self, 'video_quality'):
            quality = self.video_quality.get()
            if quality == self.t("high_quality"):
                cmd.extend(["-crf", "18", "-preset", "slow"])
            elif quality == self.t("medium_quality"):
                cmd.extend(["-crf", "23", "-preset", "medium"])
            elif quality == self.t("low_quality"):
                cmd.extend(["-crf", "28", "-preset", "fast"])
        
        # 自定义参数
        if hasattr(self, 'custom_args') and self.custom_args.get():
            custom_args_list = self.custom_args.get().split()
            cmd.extend(custom_args_list)
        
        cmd.append(self.output_file.get())
        return cmd

    def update_preview(self):
        """更新命令预览"""
        cmd = self.build_ffmpeg_command()
        self.command_preview.delete(1.0, tk.END)
        if cmd:
            self.command_preview.insert(1.0, " ".join(cmd))
    
    def check_completion_status(self):
        """检查处理是否真正完成"""
        if not self.is_processing:
            # 如果处理已经停止，重置状态并返回
            self.waiting_label.config(text="")
            return True
        
        # 检查输出文件是否存在且大小稳定
        output_file = self.output_file.get()
        if os.path.exists(output_file):
            # 获取文件大小
            current_size = os.path.getsize(output_file)
        
            # 等待一小段时间再次检查
            self.root.after(1000, lambda: self.verify_file_stable(output_file, current_size))
            return False
        else:
            # 文件还不存在，继续等待
            self.root.after(1000, self.check_completion_status)
            return False
    
    def verify_file_stable(self, file_path, previous_size):
        """验证文件大小是否稳定"""
        if not self.is_processing:
            # 如果处理已经停止，重置状态并返回
            self.waiting_label.config(text="")
            return
        
        current_size = os.path.getsize(file_path)
    
        if current_size == previous_size:
            # 文件大小稳定，处理可能已完成
            self.progress_check_count += 1
        
            if self.progress_check_count >= 2:  # 连续2次检查大小不变
                # 确认处理完成
                self.is_processing = False
                self.on_processing_complete()
            else:
                # 再检查一次
                self.root.after(1000, lambda: self.verify_file_stable(file_path, current_size))
        else:
            # 文件大小仍在变化，继续等待
            self.progress_check_count = 0
            self.root.after(1000, self.check_completion_status)
    
    def on_processing_complete(self):
        """处理真正完成"""
        self.status_label.config(text=self.t("completed"))
        self.waiting_label.config(text="")
        self.process_btn.config(text=self.t("start_processing"))
        # 重置进度条
        self.progress_var.set(100)
        self.progress_percent.set("100%")
        self.estimated_time_label.config(text=f"{self.t('estimated_time')}: 0秒")
        messagebox.showinfo(self.t("success"), self.t("completed"))
    
    def simulate_progress(self):
        """模拟进度更新（实际应用中应该从FFmpeg输出中获取真实进度）"""
        current_progress = self.progress_var.get()
    
        if current_progress < 99 and self.is_processing:
            # 模拟进度增加，但不超过99%
            new_progress = min(current_progress + 2, 99)
            self.progress_var.set(new_progress)
            self.progress_percent.set(f"{int(new_progress)}%")
        
            # 更新预计时间（简化模拟）
            remaining = (100 - new_progress) / 2
            self.estimated_time_label.config(text=f"{self.t('estimated_time')}: {remaining:.0f}秒")
        
            # 继续更新
            self.root.after(500, self.simulate_progress)
         
        elif current_progress >= 99 and self.is_processing:
            # 进度达到99%，开始检查是否真正完成
            if not self.waiting_for_completion:
                self.waiting_for_completion = True
                self.waiting_label.config(text=self.t("finalizing_processing"))
                self.progress_check_count = 0
            
                # 等待2秒后开始检查完成状态
                self.root.after(2000, self.check_completion_status)
    
    def run_ffmpeg_command(self, cmd):
        """运行FFmpeg命令"""
        try:
            self.update_preview()
            self.status_label.config(text=self.t("processing"))
        
            # 重置状态
            self.waiting_for_completion = False
            self.progress_check_count = 0
            self.waiting_label.config(text="")
        
            # 开始进度模拟
            self.progress_var.set(0)
            self.progress_percent.set("0%")
            self.processing_file_label.config(text=f"{self.t('processing_file')}: {os.path.basename(self.input_file.get())}")
            self.simulate_progress()
        
            # 运行FFmpeg命令
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
            # 如果命令成功完成，但进度模拟还未结束，等待进度模拟完成
            if self.is_processing:
                # 设置进度为99%，让模拟进度逻辑处理完成
                self.progress_var.set(99)
                self.progress_percent.set("99%")
                self.estimated_time_label.config(text=f"{self.t('estimated_time')}: 1秒")
            
        except subprocess.CalledProcessError as e:
            self.is_processing = False
            self.status_label.config(text=self.t("failed"))
            self.waiting_label.config(text="")
            self.progress_var.set(0)
            self.progress_percent.set("0%")
            messagebox.showerror(self.t("error"), f"{self.t('failed')}:\n{e.stderr}")
            return False
        except Exception as e:
            self.is_processing = False
            self.status_label.config(text=self.t("failed"))
            self.waiting_label.config(text="")
            self.progress_var.set(0)
            self.progress_percent.set("0%")
            messagebox.showerror(self.t("error"), f"{self.t('failed')}: {str(e)}")
            return False
    
    def start_processing(self):
        """开始处理"""
        if self.is_processing:
            return
        
        if not self.input_file.get() or not self.output_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_output"))
            return
    
        # 重置所有状态变量
        self.is_processing = True
        self.waiting_for_completion = False
        self.progress_check_count = 0
        self.progress_var.set(0)
        self.progress_percent.set("0%")
        self.waiting_label.config(text="")
    
        self.process_btn.config(text=self.t("processing"))
    
        # 在新线程中运行FFmpeg命令，避免界面冻结
        cmd = self.build_ffmpeg_command()
        if cmd:
            thread = threading.Thread(target=self.run_ffmpeg_command, args=(cmd,))
            thread.daemon = True
            thread.start()
    
    def convert_format(self):
        """格式转换功能"""
        if not self.input_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_file"))
            return
    
        input_file = self.input_file.get()
    
        # 检查是否是NCM转MP3
        if self.format_var.get() == "ncm_to_mp3":
            if not input_file.lower().endswith('.ncm'):
              messagebox.showwarning("警告", "NCM转MP3功能只能处理.ncm文件")
              return
        
           # 设置输出文件
            if not self.output_file.get():
                base, _ = os.path.splitext(input_file)
                self.output_file.set(base + ".mp3")
        
            # 执行NCM转MP3
            self.convert_ncm_to_mp3()
            return
    
        # 原有的格式转换逻辑
        if self.output_file.get():
            base, _ = os.path.splitext(self.output_file.get())
            self.output_file.set(base + "." + self.format_var.get())
    
        self.start_processing()

    def apply_video_processing(self):
        """应用视频处理"""
        self.start_processing()
    
    def apply_audio_processing(self):
        """应用音频处理"""
        self.start_processing()
    
    def extract_audio(self):
        """提取音频"""
        if not self.input_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_file"))
            return
        
        output_path = filedialog.asksaveasfilename(
            title=self.t("extract_audio"),
            defaultextension=".mp3",
            filetypes=[("MP3文件", "*.mp3"), ("WAV文件", "*.wav"), ("所有文件", "*.*")]
        )
        
        if output_path:
            self.output_file.set(output_path)
            cmd = ["ffmpeg", "-i", self.input_file.get(), "-vn", "-c:a", "mp3", "-b:a", "192k", "-y", output_path]
            self.run_ffmpeg_command(cmd)
    
    def extract_video(self):
        """提取视频（无音频）"""
        if not self.input_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_file"))
            return
        
        output_path = filedialog.asksaveasfilename(
            title=self.t("extract_video"),
            defaultextension=".mp4",
            filetypes=[("MP4文件", "*.mp4"), ("所有文件", "*.*")]
        )
        
        if output_path:
            self.output_file.set(output_path)
            cmd = ["ffmpeg", "-i", self.input_file.get(), "-an", "-c:v", "copy", "-y", output_path]
            self.run_ffmpeg_command(cmd)
    
    def compress_media(self):
        """压缩媒体文件"""
        if not self.input_file.get():
            messagebox.showerror(self.t("error"), self.t("select_input_file"))
            return
        
        self.video_quality.set(self.t("medium_quality"))
        self.audio_quality.set(self.t("medium_quality"))
        self.start_processing()
    
    def run_custom_command(self):
        """运行自定义命令"""
        self.start_processing()
    
    def apply_preset(self, event):
        """应用预设配置"""
        preset = self.preset_var.get()
        
        if preset == self.t("high_quality_mp4"):
            self.format_var.set("mp4")
            self.video_codec.set("libx264")
            self.audio_codec.set("aac")
            self.video_quality.set(self.t("high_quality"))
            self.audio_quality.set(self.t("high_quality"))
        elif preset == self.t("high_quality_mp3"):
            self.format_var.set("mp3")
            self.audio_codec.set("libmp3lame")
            self.audio_bitrate.set("320k")
        elif preset == self.t("web_optimized"):
            self.format_var.set("mp4")
            self.video_codec.set("libx264")
            self.audio_codec.set("aac")
            self.resolution.set("1280x720")
            self.video_quality.set(self.t("medium_quality"))
        elif preset == self.t("mobile_optimized"):
            self.format_var.set("mp4")
            self.video_codec.set("libx264")
            self.audio_codec.set("aac")
            self.resolution.set("854x480")
            self.video_quality.set(self.t("medium_quality"))

def main():
    root = tk.Tk()
    app = FFmpegGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()