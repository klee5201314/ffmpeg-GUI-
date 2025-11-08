import json
import os
import re
import subprocess
import sys
import threading
import time
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

try:
    from ncmdump import dump
    NCM_AVAILABLE = True
except ImportError:
    NCM_AVAILABLE = False

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QCheckBox,
    QProgressBar, QTabWidget, QGroupBox, QMessageBox,
    QFileDialog, QDialog, QGridLayout
)


class Config:
    """配置常量"""
    VERSION = "V0.2"
    SUPPORTED_VIDEO_FORMATS = "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv *.m4v"
    SUPPORTED_AUDIO_FORMATS = "*.mp3 *.wav *.flac *.aac *.m4a *.ogg *.wma *.ncm"
    DEFAULT_RESOLUTIONS = ["3840x2160", "1920x1080", "1280x720", "854x480", "640x360"]
    DEFAULT_FPS = ["60", "30", "25", "24", "15"]
    DEFAULT_SAMPLE_RATES = ["44100", "48000", "22050", "16000"]
    DEFAULT_BITRATES = ["64k", "128k", "192k", "256k", "320k"]
    DEFAULT_CHANNELS = ["1", "2", "6", "8"]



class SplashScreen(QDialog):
    """启动界面"""
    
    def __init__(self, language_manager):
        super().__init__()
        self.language_manager = language_manager
        self.setWindowTitle("FFmpeg GUI")
        self.setFixedSize(400, 250)  # 增加高度以显示更多信息
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog { background-color: #f0f0f0; }
            QLabel { background-color: transparent; }
        """)
        
        # 居中显示
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("🎬 FFmpeg 媒体处理工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # 版本信息
        version_label = QLabel("版本 V0.2")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(QFont("Arial", 10))
        layout.addWidget(version_label)
        
        # 状态标签
        self.status_label = QLabel("正在初始化...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 10))
        layout.addWidget(self.status_label)
        
        # 详细信息
        self.detail_label = QLabel("")
        self.detail_label.setAlignment(Qt.AlignCenter)
        self.detail_label.setFont(QFont("Arial", 8))
        self.detail_label.setStyleSheet("color: gray;")
        layout.addWidget(self.detail_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定模式
        layout.addWidget(self.progress_bar)
        
        # 版权信息
        copyright_label = QLabel("© 2024 FFmpeg GUI Tool")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setFont(QFont("Arial", 8))
        layout.addWidget(copyright_label)
        
        self.setLayout(layout)
    
    def update_status(self, text, detail=""):
        self.status_label.setText(text)
        self.detail_label.setText(detail)
        QApplication.processEvents()


class LanguageManager:
    """语言管理器"""
    
    def __init__(self):
        self.languages = {}
        self.current_dir = Path(__file__).parent
        self.load_languages()
    
    def load_languages(self) -> None:
        locales_dir = self.current_dir / "locales"
        
        if not locales_dir.exists():
            locales_dir.mkdir(parents=True, exist_ok=True)
            self.create_default_locales(locales_dir)
        
        for json_file in locales_dir.glob("*.json"):
            lang_code = json_file.stem
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    self.languages[lang_code] = json.load(f)
            except Exception as e:
                print(f"加载语言文件 {json_file} 失败: {e}")
        
        if not self.languages:
            self.languages = self.get_default_languages()
    
    def create_default_locales(self, locales_dir: Path) -> None:
        default_languages = self.get_default_languages()
        
        for lang_code, translations in default_languages.items():
            file_path = locales_dir / f"{lang_code}.json"
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(translations, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"创建语言文件 {file_path} 失败: {e}")
    
    def get_default_languages(self) -> Dict[str, Dict[str, str]]:
        return {
            "zh_CN": self._get_chinese_translations(),
            "en_US": self._get_english_translations()
        }
    
    def _get_chinese_translations(self) -> Dict[str, str]:
        return {
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
            "ncm_to_mp3": "🎵 NCM转MP3",
            "video_encoding": "🎬 视频编码",
            "video_encoder": "🔧 视频编码器:",
            "resolution": "📐 分辨率:",
            "fps": "🎞️ 帧率:",
            "original_resolution": "原分辨率",
            "original_fps": "原帧率",
            "custom_resolution": "自定义分辨率",
            "custom_fps": "自定义帧率",
            "custom_sample_rate": "自定义采样率",
            "custom_bitrate": "自定义比特率",
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
            "switch_to_english": "🇺🇸 英文",
            "switch_to_chinese": "🇨🇳 中文",
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
            "finalizing_processing": "⏳ 正在完成处理...",
            "recommended_values": "💡 推荐值",
            "custom_value": "自定义",
            "width_x_height": "宽x高 (如: 1920x1080)",
            "fps_value": "帧率值 (如: 30)",
            "sample_rate_value": "采样率值 (如: 44100)",
            "bitrate_value": "比特率值 (如: 128k)",
            "invalid_value": "❌ 无效值",
            "valid_resolution_format": "请输入有效的分辨率格式: 宽x高",
            "valid_number": "请输入有效的数字",
            "valid_bitrate_format": "请输入有效的比特率格式 (如: 128k, 1.5M)",
            "language_switching": "🔄 切换语言中...",
            "ncm_decryption": "🔓 NCM文件解密",
            "decrypting_ncm": "🔓 正在解密NCM文件...",
            "ncm_decryption_success": "✅ NCM文件解密成功",
            "ncm_decryption_failed": "❌ NCM文件解密失败",
            "converting_to_mp3": "🔄 正在转换为MP3...",
            "ncm_conversion_complete": "✅ NCM转MP3完成"
        }
    
    def _get_english_translations(self) -> Dict[str, str]:
        return {
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
            "ncm_to_mp3": "🎵 NCM to MP3",
            "video_encoding": "🎬 Video Encoding",
            "video_encoder": "🔧 Video Encoder:",
            "resolution": "📐 Resolution:",
            "fps": "🎞️ Frame Rate:",
            "original_resolution": "Original Resolution",
            "original_fps": "Original FPS",
            "custom_resolution": "Custom Resolution",
            "custom_fps": "Custom FPS",
            "custom_sample_rate": "Custom Sample Rate",
            "custom_bitrate": "Custom Bitrate",
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
            "switch_to_english": "🇺🇸 English",
            "switch_to_chinese": "🇨🇳 Chinese",
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
            "finalizing_processing": "⏳ Finalizing processing...",
            "recommended_values": "💡 Recommended Values",
            "custom_value": "Custom",
            "width_x_height": "Width x Height (e.g.: 1920x1080)",
            "fps_value": "FPS Value (e.g.: 30)",
            "sample_rate_value": "Sample Rate Value (e.g.: 44100)",
            "bitrate_value": "Bitrate Value (e.g.: 128k)",
            "invalid_value": "❌ Invalid Value",
            "valid_resolution_format": "Please enter valid resolution format: width x height",
            "valid_number": "Please enter a valid number",
            "valid_bitrate_format": "Please enter valid bitrate format (e.g.: 128k, 1.5M)",
            "language_switching": "🔄 Switching language...",
            "ncm_decryption": "🔓 NCM File Decryption",
            "decrypting_ncm": "🔓 Decrypting NCM file...",
            "ncm_decryption_success": "✅ NCM file decryption successful",
            "ncm_decryption_failed": "❌ NCM file decryption failed",
            "converting_to_mp3": "🔄 Converting to MP3...",
            "ncm_conversion_complete": "✅ NCM to MP3 conversion complete"
        }
    
    def get_available_languages(self) -> List[str]:
        return list(self.languages.keys())
    
    def get_language_name(self, lang_code: str) -> str:
        names = {"zh_CN": "🇨🇳 中文", "en_US": "🇺🇸 English"}
        return names.get(lang_code, lang_code)
    
    def get_text(self, language: str, key: str) -> str:
        return self.languages.get(language, {}).get(key, key)


class HardwareDetector:
    """硬件检测器"""
    
    def __init__(self, language_manager: LanguageManager):
        self.language_manager = language_manager
        self.hardware_acceleration = {}
        self.hardware_encoders = {}
    
    def detect_all(self) -> None:
        self.detect_hardware_acceleration()
        self.detect_hardware_encoders()
    
    def detect_hardware_acceleration(self) -> None:
        self.hardware_acceleration = {}
        
        hwaccels_to_check = {
            "cuda": "NVIDIA CUDA",
            "qsv": "Intel Quick Sync", 
            "vaapi": "VA-API",
            "d3d11va": "Direct3D 11",
            "videotoolbox": "Apple VideoToolbox",
            "amf": "AMD AMF"
        }
        
        try:
            result = subprocess.run(
                ["ffmpeg", "-hwaccels"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                for hwaccel, display_name in hwaccels_to_check.items():
                    self.hardware_acceleration[hwaccel] = {
                        "name": display_name,
                        "supported": hwaccel in output
                    }
            else:
                self._mark_all_unsupported(hwaccels_to_check)
                
        except (subprocess.TimeoutExpired, Exception) as e:
            print(f"硬件加速检测失败: {e}")
            self._mark_all_unsupported(hwaccels_to_check)
    
    def detect_hardware_encoders(self) -> None:
        self.hardware_encoders = {}
        
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
            result = subprocess.run(
                ["ffmpeg", "-encoders"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                for encoder, display_name in encoder_mapping.items():
                    # 使用更灵活的正则匹配
                    pattern = rf'^\s*V\S*\s+{encoder}\s'
                    self.hardware_encoders[encoder] = {
                        "name": display_name,
                        "supported": bool(re.search(pattern, output, re.MULTILINE))
                    }
            else:
                self._mark_all_encoders_unsupported(encoder_mapping)
                
        except Exception as e:
            print(f"硬件编码器检测失败: {e}")
            self._mark_all_encoders_unsupported(encoder_mapping)
    
    def get_hwaccel_options(self) -> List[str]:
        options = [self._t("hwaccel_none")]
        for hwaccel, info in self.hardware_acceleration.items():
            if info["supported"]:
                options.append(info["name"])
        return options
    
    def get_supported_video_codecs(self) -> List[str]:
        # 基础软件编码器
        codecs = ["libx264", "libx265", "mpeg4", "vp9", "copy"]
        
        # 添加支持的硬件编码器
        for encoder, info in self.hardware_encoders.items():
            if info["supported"]:
                codecs.append(encoder)
        
        return codecs
    
    def get_hardware_status_text(self) -> str:
        hwaccel_count = sum(1 for info in self.hardware_acceleration.values() if info["supported"])
        encoder_count = sum(1 for info in self.hardware_encoders.values() if info["supported"])
        
        if hwaccel_count == 0 and encoder_count == 0:
            return self._t("no_hardware_support")
        else:
            return f"{self._t('hardware_support_detected')} ({hwaccel_count}个加速器, {encoder_count}个编码器)"
    
    def get_hardware_encoders_text(self) -> str:
        supported_encoders = []
        for encoder, info in self.hardware_encoders.items():
            if info["supported"]:
                supported_encoders.append(f"✅ {info['name']} ({encoder})")
        
        if not supported_encoders:
            return self._t("no_hardware_support")
        else:
            return "\n".join(supported_encoders)
    
    def get_hardware_accel_text(self) -> str:
        supported_accels = []
        for hwaccel, info in self.hardware_acceleration.items():
            if info["supported"]:
                supported_accels.append(f"✅ {info['name']}")
        
        if not supported_accels:
            return self._t("no_hardware_support")
        else:
            return "\n".join(supported_accels)
    
    def _mark_all_unsupported(self, hwaccels_to_check: Dict[str, str]) -> None:
        for hwaccel, display_name in hwaccels_to_check.items():
            self.hardware_acceleration[hwaccel] = {
                "name": display_name,
                "supported": False
            }
    
    def _mark_all_encoders_unsupported(self, encoder_mapping: Dict[str, str]) -> None:
        for encoder, display_name in encoder_mapping.items():
            self.hardware_encoders[encoder] = {
                "name": display_name,
                "supported": False
            }
    
    def _t(self, key: str) -> str:
        return self.language_manager.get_text("zh_CN", key)


class NCMDecoder:
    """NCM文件解码器"""
    
    @staticmethod
    def decrypt_ncm_file(ncm_file_path: str) -> str:
        if not NCM_AVAILABLE:
            raise Exception("ncmdump库未安装，无法解密NCM文件")
        
        try:
            temp_dir = tempfile.gettempdir()
            output_filename = f"ncm_decrypted_{uuid.uuid4().hex}"
            output_path = os.path.join(temp_dir, output_filename)
            
            dump(ncm_file_path, output_path)
            
            if os.path.exists(output_path):
                return output_path
            else:
                raise Exception("解密后的文件未生成")
                
        except Exception as e:
            raise Exception(f"NCM文件解密失败: {str(e)}")


class FFmpegCommandBuilder:
    """FFmpeg命令构建器"""
    
    def __init__(self, language_manager: LanguageManager):
        self.language_manager = language_manager
    
    def build_command(self, params: Dict[str, Any]) -> List[str]:
        cmd = ["ffmpeg"]
        
        # 硬件加速器设置（必须在输入文件之前）
        hwaccel_display = params.get("hwaccel", "")
        hwaccel_internal = self._get_hwaccel_internal_name(hwaccel_display)
        if hwaccel_internal:
            cmd.extend(["-hwaccel", hwaccel_internal])
        
        # 输入文件
        cmd.extend(["-i", params["input_file"]])
        
        # 覆盖输出文件
        cmd.append("-y")
        
        # 视频编码参数
        if params.get("video_codec") and params["video_codec"] != "copy":
            cmd.extend(["-c:v", params["video_codec"]])
        
        # 分辨率设置
        if resolution := self._get_resolution(params):
            cmd.extend(["-s", resolution])
        
        # 帧率设置
        if fps := self._get_fps(params):
            cmd.extend(["-r", fps])
        
        # 音频编码参数
        if audio_codec := params.get("audio_codec"):
            cmd.extend(["-c:a", audio_codec])
        
        # 采样率设置
        if sample_rate := self._get_sample_rate(params):
            cmd.extend(["-ar", sample_rate])
        
        # 声道数设置
        if channels := params.get("channels"):
            cmd.extend(["-ac", channels])
        
        # 比特率设置
        if bitrate := self._get_bitrate(params):
            cmd.extend(["-b:a", bitrate])
        
        # 视频滤镜
        if vf_filters := self._build_video_filters(params):
            cmd.extend(["-vf", ",".join(vf_filters)])
        
        # 音频滤镜
        if af_filters := self._build_audio_filters(params):
            cmd.extend(["-af", ",".join(af_filters)])
        
        # 质量设置
        if quality_params := self._get_quality_params(params):
            cmd.extend(quality_params)
        
        # 自定义参数
        if custom_args := params.get("custom_args"):
            cmd.extend(custom_args.split())
        
        cmd.append(params["output_file"])
        return cmd
    
    def _get_hwaccel_internal_name(self, hwaccel_display: str) -> Optional[str]:
        """获取硬件加速器内部名称"""
        if hwaccel_display == self._t("hwaccel_none") or not hwaccel_display:
            return None
        
        # 将显示名称映射回FFmpeg内部名称
        hwaccel_mapping = {
            self._t("hwaccel_cuda"): "cuda",
            self._t("hwaccel_qsv"): "qsv", 
            self._t("hwaccel_vaapi"): "vaapi",
            self._t("hwaccel_d3d11va"): "d3d11va",
            self._t("hwaccel_videotoolbox"): "videotoolbox",
            self._t("hwaccel_amf"): "amf"
        }
        
        return hwaccel_mapping.get(hwaccel_display)
    
    def _get_resolution(self, params: Dict[str, Any]) -> Optional[str]:
        resolution = params.get("resolution", "")
        custom_resolution = params.get("custom_resolution", "")
        
        if resolution == self._t("custom_resolution") and custom_resolution:
            return custom_resolution
        elif resolution not in [self._t("original_resolution"), self._t("custom_resolution")]:
            return resolution
        return None
    
    def _get_fps(self, params: Dict[str, Any]) -> Optional[str]:
        fps = params.get("fps", "")
        custom_fps = params.get("custom_fps", "")
        
        if fps == self._t("custom_fps") and custom_fps:
            return custom_fps
        elif fps not in [self._t("original_fps"), self._t("custom_fps")]:
            return fps
        return None
    
    def _get_sample_rate(self, params: Dict[str, Any]) -> Optional[str]:
        sample_rate = params.get("sample_rate", "")
        custom_sample_rate = params.get("custom_sample_rate", "")
        
        if sample_rate == self._t("custom_sample_rate") and custom_sample_rate:
            return custom_sample_rate
        elif sample_rate != self._t("custom_sample_rate"):
            return sample_rate
        return None
    
    def _get_bitrate(self, params: Dict[str, Any]) -> Optional[str]:
        bitrate = params.get("bitrate", "")
        custom_bitrate = params.get("custom_bitrate", "")
        
        if bitrate == self._t("custom_bitrate") and custom_bitrate:
            return custom_bitrate
        elif bitrate != self._t("custom_bitrate"):
            return bitrate
        return None
    
    def _build_video_filters(self, params: Dict[str, Any]) -> List[str]:
        filters = []
        
        if params.get("crop_enabled"):
            filters.append(f"crop={params.get('crop_params', 'iw:ih:0:0')}")
        
        if params.get("scale_enabled"):
            if resolution := self._get_resolution(params):
                filters.append(f"scale={resolution.replace('x', ':')}")
        
        if params.get("rotate_enabled"):
            filters.append(f"transpose={params.get('rotate_angle', '90')}")
        
        return filters
    
    def _build_audio_filters(self, params: Dict[str, Any]) -> List[str]:
        filters = []
        
        if params.get("volume_enabled"):
            filters.append(f"volume={params.get('volume_factor', '1.0')}")
        
        return filters
    
    def _get_quality_params(self, params: Dict[str, Any]) -> List[str]:
        video_quality = params.get("video_quality", "")
        
        if video_quality == self._t("high_quality"):
            return ["-crf", "18", "-preset", "slow"]
        elif video_quality == self._t("medium_quality"):
            return ["-crf", "23", "-preset", "medium"]
        elif video_quality == self._t("low_quality"):
            return ["-crf", "28", "-preset", "fast"]
        
        return []
    
    def _t(self, key: str) -> str:
        return self.language_manager.get_text("zh_CN", key)


class FFmpegWorker(QThread):
    """FFmpeg工作线程"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, command: List[str]):
        super().__init__()
        self.command = command
        self.is_running = True
    
    def run(self) -> None:
        try:
            self.status_updated.emit("处理中...")
            
            process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            for line in process.stdout:
                if not self.is_running:
                    process.terminate()
                    break
            
            process.wait()
            
            if process.returncode == 0:
                self.finished_signal.emit(True, "处理完成")
            else:
                self.finished_signal.emit(False, f"处理失败，返回码: {process.returncode}")
                
        except Exception as e:
            self.finished_signal.emit(False, f"处理异常: {str(e)}")
    
    def stop(self) -> None:
        self.is_running = False


class FileProcessor:
    """文件处理器"""
    
    @staticmethod
    def get_file_info(filename: str) -> str:
        try:
            if filename.lower().endswith('.ncm'):
                return FileProcessor._get_ncm_file_info(filename)
            else:
                return FileProcessor._get_media_file_info(filename)
        except Exception as e:
            return f"❌ 无法获取文件信息: {str(e)}"
    
    @staticmethod
    def _get_ncm_file_info(filename: str) -> str:
        info = []
        info.append("🎵 NCM加密音频文件")
        info.append(f"📄 文件: {os.path.basename(filename)}")
        info.append(f"📁 路径: {filename}")
        
        try:
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            info.append(f"💾 大小: {size_mb:.2f} MB")
        except Exception:
            info.append("💾 大小: 无法读取")
        
        info.append("🔓 状态: 加密文件，需要解密")
        return "\n".join(info)
    
    @staticmethod
    def _get_media_file_info(filename: str) -> str:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", 
                 "-show_format", "-show_streams", filename],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=True
            )
            
            info = json.loads(result.stdout or "{}")
            return FileProcessor._format_media_info(info, filename)
            
        except Exception as e:
            return f"❌ 无法获取文件信息: {str(e)}"
    
    @staticmethod
    def _format_media_info(info: Dict, filename: str) -> str:
        lines = []
        lines.append(f"📄 文件: {os.path.basename(filename)}")
        lines.append(f"📁 路径: {filename}")
        
        try:
            size_mb = os.path.getsize(filename) / (1024 * 1024)
            lines.append(f"💾 大小: {size_mb:.2f} MB")
        except Exception:
            lines.append("💾 大小: 无法读取")
        
        if 'format' in info and info['format']:
            format_info = info['format']
            lines.append(f"📋 格式: {format_info.get('format_name', '未知')}")
            
            duration = float(format_info.get('duration', 0) or 0)
            lines.append(f"⏱️ 时长: {duration:.2f} 秒")
            
            try:
                bit_rate = int(format_info.get('bit_rate', 0) or 0)
                lines.append(f"📊 比特率: {bit_rate / 1000:.0f} kbps")
            except Exception:
                pass
        
        if 'streams' in info and info['streams']:
            video_streams = [s for s in info['streams'] if s.get('codec_type') == 'video']
            audio_streams = [s for s in info['streams'] if s.get('codec_type') == 'audio']
            
            if video_streams:
                video = video_streams[0]
                lines.append(f"🎥 视频: {video.get('codec_name', '未知')}")
                lines.append(f"📐 分辨率: {video.get('width', '未知')}x{video.get('height', '未知')}")
                lines.append(f"🎞️ 帧率: {video.get('r_frame_rate', '未知')}")
            
            if audio_streams:
                audio = audio_streams[0]
                lines.append(f"🎵 音频: {audio.get('codec_name', '未知')}")
                lines.append(f"🔊 声道: {audio.get('channels', '未知')}")
                lines.append(f"🎚️ 采样率: {audio.get('sample_rate', '未知')} Hz")
        
        return "\n".join(lines)


class BaseTabWidget(QWidget):
    """基础标签页组件"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__()
        self.language_manager = language_manager
        self.current_language = "zh_CN"
    
    def t(self, key: str) -> str:
        return self.language_manager.get_text(self.current_language, key)
    
    def update_language(self, language: str) -> None:
        self.current_language = language
        self.retranslate_ui()
    
    def retranslate_ui(self) -> None:
        pass


class FileOperationsTab(BaseTabWidget):
    """文件操作标签页"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__(language_manager)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 文件操作区域
        self.file_operations_group = QGroupBox(self.t("file_operations"))
        file_layout = QVBoxLayout(self.file_operations_group)
        
        # 输入文件
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel(self.t("source_file")))
        self.input_file_edit = QLineEdit()
        input_layout.addWidget(self.input_file_edit)
        self.input_browse_btn = QPushButton(self.t("browse"))
        input_layout.addWidget(self.input_browse_btn)
        file_layout.addLayout(input_layout)
        
        # 输出文件
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel(self.t("output_file")))
        self.output_file_edit = QLineEdit()
        output_layout.addWidget(self.output_file_edit)
        self.output_browse_btn = QPushButton(self.t("browse"))
        output_layout.addWidget(self.output_browse_btn)
        file_layout.addLayout(output_layout)
        
        layout.addWidget(self.file_operations_group)
        
        # 文件信息区域
        self.file_info_group = QGroupBox(self.t("file_info"))
        info_layout = QVBoxLayout(self.file_info_group)
        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        info_layout.addWidget(self.file_info_text)
        layout.addWidget(self.file_info_group)
        
        layout.addStretch()
    
    def retranslate_ui(self) -> None:
        self.file_operations_group.setTitle(self.t("file_operations"))
        self.file_info_group.setTitle(self.t("file_info"))
        self.input_browse_btn.setText(self.t("browse"))
        self.output_browse_btn.setText(self.t("browse"))


class FormatConversionTab(BaseTabWidget):
    """格式转换标签页"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__(language_manager)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 格式转换
        self.format_conversion_group = QGroupBox(self.t("format_conversion"))
        convert_layout = QHBoxLayout(self.format_conversion_group)
        
        convert_layout.addWidget(QLabel(self.t("output_format")))
        self.format_combo = QComboBox()
        formats = ["mp4", "avi", "mov", "mkv", "webm", "mp3", "wav", "flac", "aac", "m4a", "ncm_to_mp3"]
        self.format_combo.addItems(formats)
        convert_layout.addWidget(self.format_combo)
        
        self.convert_btn = QPushButton(self.t("convert_format"))
        convert_layout.addWidget(self.convert_btn)
        
        layout.addWidget(self.format_conversion_group)
        
        # 质量设置
        self.quality_settings_group = QGroupBox(self.t("quality_settings"))
        quality_layout = QGridLayout(self.quality_settings_group)
        
        quality_layout.addWidget(QLabel(self.t("video_quality")), 0, 0)
        self.video_quality_combo = QComboBox()
        qualities = [self.t("high_quality"), self.t("medium_quality"), self.t("low_quality"), self.t("original_quality")]
        self.video_quality_combo.addItems(qualities)
        quality_layout.addWidget(self.video_quality_combo, 0, 1)
        
        quality_layout.addWidget(QLabel(self.t("audio_quality")), 1, 0)
        self.audio_quality_combo = QComboBox()
        self.audio_quality_combo.addItems(qualities)
        quality_layout.addWidget(self.audio_quality_combo, 1, 1)
        
        layout.addWidget(self.quality_settings_group)
        
        # 快速操作
        self.quick_actions_group = QGroupBox(self.t("quick_actions"))
        quick_layout = QVBoxLayout(self.quick_actions_group)
        
        self.extract_audio_btn = QPushButton(self.t("extract_audio"))
        quick_layout.addWidget(self.extract_audio_btn)
        
        self.ncm_to_mp3_btn = QPushButton(self.t("ncm_to_mp3"))
        quick_layout.addWidget(self.ncm_to_mp3_btn)
        
        self.extract_video_btn = QPushButton(self.t("extract_video"))
        quick_layout.addWidget(self.extract_video_btn)
        
        self.compress_media_btn = QPushButton(self.t("compress_media"))
        quick_layout.addWidget(self.compress_media_btn)
        
        layout.addWidget(self.quick_actions_group)
        
        layout.addStretch()
    
    def retranslate_ui(self) -> None:
        self.format_conversion_group.setTitle(self.t("format_conversion"))
        self.quality_settings_group.setTitle(self.t("quality_settings"))
        self.quick_actions_group.setTitle(self.t("quick_actions"))
        
        self.convert_btn.setText(self.t("convert_format"))
        self.extract_audio_btn.setText(self.t("extract_audio"))
        self.ncm_to_mp3_btn.setText(self.t("ncm_to_mp3"))
        self.extract_video_btn.setText(self.t("extract_video"))
        self.compress_media_btn.setText(self.t("compress_media"))
        
        # 更新质量选项
        qualities = [self.t("high_quality"), self.t("medium_quality"), self.t("low_quality"), self.t("original_quality")]
        current_video = self.video_quality_combo.currentText()
        current_audio = self.audio_quality_combo.currentText()
        
        self.video_quality_combo.clear()
        self.video_quality_combo.addItems(qualities)
        self.audio_quality_combo.clear()
        self.audio_quality_combo.addItems(qualities)
        
        # 恢复选择
        if current_video in qualities:
            self.video_quality_combo.setCurrentText(current_video)
        if current_audio in qualities:
            self.audio_quality_combo.setCurrentText(current_audio)


class VideoProcessingTab(BaseTabWidget):
    """视频处理标签页"""
    
    def __init__(self, language_manager: LanguageManager, hardware_detector: HardwareDetector):
        super().__init__(language_manager)
        self.hardware_detector = hardware_detector
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 视频编码设置
        self.video_encoding_group = QGroupBox(self.t("video_encoding"))
        video_layout = QGridLayout(self.video_encoding_group)
        
        video_layout.addWidget(QLabel(self.t("video_encoder")), 0, 0)
        self.video_codec_combo = QComboBox()
        codecs = self.hardware_detector.get_supported_video_codecs()
        self.video_codec_combo.addItems(codecs)
        video_layout.addWidget(self.video_codec_combo, 0, 1)
        
        video_layout.addWidget(QLabel(self.t("resolution")), 1, 0)
        self.resolution_combo = QComboBox()
        resolutions = [self.t("original_resolution"), self.t("custom_resolution")] + Config.DEFAULT_RESOLUTIONS
        self.resolution_combo.addItems(resolutions)
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        video_layout.addWidget(self.resolution_combo, 1, 1)
        
        # 自定义分辨率
        self.custom_resolution_widget = QWidget()
        self.custom_resolution_layout = QHBoxLayout(self.custom_resolution_widget)
        self.custom_resolution_layout.addWidget(QLabel(self.t("width_x_height")))
        self.custom_resolution_edit = QLineEdit()
        self.custom_resolution_layout.addWidget(self.custom_resolution_edit)
        self.custom_resolution_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.addWidget(self.custom_resolution_widget, 2, 0, 1, 2)
        self.custom_resolution_widget.setVisible(False)
        
        video_layout.addWidget(QLabel(self.t("fps")), 3, 0)
        self.fps_combo = QComboBox()
        fps_values = [self.t("original_fps"), self.t("custom_fps")] + Config.DEFAULT_FPS
        self.fps_combo.addItems(fps_values)
        self.fps_combo.currentTextChanged.connect(self.on_fps_changed)
        video_layout.addWidget(self.fps_combo, 3, 1)
        
        # 自定义帧率
        self.custom_fps_widget = QWidget()
        self.custom_fps_layout = QHBoxLayout(self.custom_fps_widget)
        self.custom_fps_layout.addWidget(QLabel(self.t("fps_value")))
        self.custom_fps_edit = QLineEdit()
        self.custom_fps_layout.addWidget(self.custom_fps_edit)
        self.custom_fps_layout.setContentsMargins(0, 0, 0, 0)
        video_layout.addWidget(self.custom_fps_widget, 4, 0, 1, 2)
        self.custom_fps_widget.setVisible(False)
        
        layout.addWidget(self.video_encoding_group)
        
        # 硬件加速选项
        self.hardware_acceleration_group = QGroupBox(self.t("hardware_acceleration"))
        hwaccel_layout = QVBoxLayout(self.hardware_acceleration_group)
        
        self.hwaccel_combo = QComboBox()
        hwaccel_options = self.hardware_detector.get_hwaccel_options()
        self.hwaccel_combo.addItems(hwaccel_options)
        hwaccel_layout.addWidget(self.hwaccel_combo)
        
        layout.addWidget(self.hardware_acceleration_group)
        
        # 视频滤镜
        self.video_filters_group = QGroupBox(self.t("video_filters"))
        filters_layout = QGridLayout(self.video_filters_group)
        
        self.crop_check = QCheckBox(self.t("crop_video"))
        filters_layout.addWidget(self.crop_check, 0, 0)
        filters_layout.addWidget(QLabel(self.t("crop_params")), 0, 1)
        self.crop_params_edit = QLineEdit("iw:ih:0:0")
        filters_layout.addWidget(self.crop_params_edit, 0, 2)
        
        self.scale_check = QCheckBox(self.t("scale_video"))
        filters_layout.addWidget(self.scale_check, 1, 0)
        
        self.rotate_check = QCheckBox(self.t("rotate_video"))
        filters_layout.addWidget(self.rotate_check, 2, 0)
        filters_layout.addWidget(QLabel(self.t("rotate_angle")), 2, 1)
        self.rotate_angle_combo = QComboBox()
        angles = ["90", "180", "270"]
        self.rotate_angle_combo.addItems(angles)
        filters_layout.addWidget(self.rotate_angle_combo, 2, 2)
        
        layout.addWidget(self.video_filters_group)
        
        self.apply_video_btn = QPushButton(self.t("apply_video_processing"))
        layout.addWidget(self.apply_video_btn)
        
        layout.addStretch()
    
    def on_resolution_changed(self, text):
        self.custom_resolution_widget.setVisible(text == self.t("custom_resolution"))
    
    def on_fps_changed(self, text):
        self.custom_fps_widget.setVisible(text == self.t("custom_fps"))
    
    def retranslate_ui(self) -> None:
        self.video_encoding_group.setTitle(self.t("video_encoding"))
        self.hardware_acceleration_group.setTitle(self.t("hardware_acceleration"))
        self.video_filters_group.setTitle(self.t("video_filters"))
        self.apply_video_btn.setText(self.t("apply_video_processing"))
        
        # 更新分辨率选项
        resolutions = [self.t("original_resolution"), self.t("custom_resolution")] + Config.DEFAULT_RESOLUTIONS
        current_res = self.resolution_combo.currentText()
        self.resolution_combo.clear()
        self.resolution_combo.addItems(resolutions)
        if current_res in resolutions:
            self.resolution_combo.setCurrentText(current_res)
        
        # 更新帧率选项
        fps_values = [self.t("original_fps"), self.t("custom_fps")] + Config.DEFAULT_FPS
        current_fps = self.fps_combo.currentText()
        self.fps_combo.clear()
        self.fps_combo.addItems(fps_values)
        if current_fps in fps_values:
            self.fps_combo.setCurrentText(current_fps)
        
        # 更新硬件加速选项
        hwaccel_options = self.hardware_detector.get_hwaccel_options()
        current_hwaccel = self.hwaccel_combo.currentText()
        self.hwaccel_combo.clear()
        self.hwaccel_combo.addItems(hwaccel_options)
        if current_hwaccel in hwaccel_options:
            self.hwaccel_combo.setCurrentText(current_hwaccel)


class AudioProcessingTab(BaseTabWidget):
    """音频处理标签页"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__(language_manager)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 音频设置
        self.audio_settings_group = QGroupBox(self.t("audio_settings"))
        audio_layout = QGridLayout(self.audio_settings_group)
        
        audio_layout.addWidget(QLabel(self.t("audio_encoder")), 0, 0)
        self.audio_codec_combo = QComboBox()
        audio_codecs = ["aac", "mp3", "flac", "opus", "copy", "libmp3lame"]
        self.audio_codec_combo.addItems(audio_codecs)
        audio_layout.addWidget(self.audio_codec_combo, 0, 1)
        
        audio_layout.addWidget(QLabel(self.t("sample_rate")), 1, 0)
        self.sample_rate_combo = QComboBox()
        sample_rates = Config.DEFAULT_SAMPLE_RATES + [self.t("custom_sample_rate")]
        self.sample_rate_combo.addItems(sample_rates)
        self.sample_rate_combo.currentTextChanged.connect(self.on_sample_rate_changed)
        audio_layout.addWidget(self.sample_rate_combo, 1, 1)
        
        # 声道数设置
        audio_layout.addWidget(QLabel(self.t("channels")), 2, 0)
        self.channels_combo = QComboBox()
        self.channels_combo.addItems(Config.DEFAULT_CHANNELS)
        audio_layout.addWidget(self.channels_combo, 2, 1)
        
        audio_layout.addWidget(QLabel(self.t("bitrate")), 3, 0)
        self.bitrate_combo = QComboBox()
        bitrates = Config.DEFAULT_BITRATES + [self.t("custom_bitrate")]
        self.bitrate_combo.addItems(bitrates)
        self.bitrate_combo.currentTextChanged.connect(self.on_bitrate_changed)
        audio_layout.addWidget(self.bitrate_combo, 3, 1)
        
        # 自定义采样率
        self.custom_sample_rate_widget = QWidget()
        self.custom_sample_rate_layout = QHBoxLayout(self.custom_sample_rate_widget)
        self.custom_sample_rate_layout.addWidget(QLabel(self.t("sample_rate_value")))
        self.custom_sample_rate_edit = QLineEdit()
        self.custom_sample_rate_edit.setValidator(QIntValidator(8000, 192000, self))
        self.custom_sample_rate_layout.addWidget(self.custom_sample_rate_edit)
        self.custom_sample_rate_layout.setContentsMargins(0, 0, 0, 0)
        audio_layout.addWidget(self.custom_sample_rate_widget, 4, 0, 1, 2)
        self.custom_sample_rate_widget.setVisible(False)
        
        # 自定义比特率
        self.custom_bitrate_widget = QWidget()
        self.custom_bitrate_layout = QHBoxLayout(self.custom_bitrate_widget)
        self.custom_bitrate_layout.addWidget(QLabel(self.t("bitrate_value")))
        self.custom_bitrate_edit = QLineEdit()
        self.custom_bitrate_edit.setPlaceholderText("如: 128k, 1.5M")
        self.custom_bitrate_layout.addWidget(self.custom_bitrate_edit)
        self.custom_bitrate_layout.setContentsMargins(0, 0, 0, 0)
        audio_layout.addWidget(self.custom_bitrate_widget, 5, 0, 1, 2)
        self.custom_bitrate_widget.setVisible(False)
        
        # 推荐值提示
        recommended_label = QLabel(self.t("recommended_values") + ":\n" +
                                  "采样率: 44100 (CD质量), 48000 (专业音频)\n" +
                                  "比特率: 128k (标准), 192k (高质量), 320k (极高)")
        recommended_label.setStyleSheet("color: blue; font-size: 9px;")
        audio_layout.addWidget(recommended_label, 6, 0, 1, 2)
        
        layout.addWidget(self.audio_settings_group)
        
        # 音频滤镜
        self.audio_filters_group = QGroupBox(self.t("audio_filters"))
        audio_filters_layout = QGridLayout(self.audio_filters_group)
        
        self.volume_check = QCheckBox(self.t("adjust_volume"))
        audio_filters_layout.addWidget(self.volume_check, 0, 0)
        audio_filters_layout.addWidget(QLabel(self.t("volume_factor")), 0, 1)
        self.volume_factor_edit = QLineEdit("1.0")
        audio_filters_layout.addWidget(self.volume_factor_edit, 0, 2)
        
        layout.addWidget(self.audio_filters_group)
        
        self.apply_audio_btn = QPushButton(self.t("apply_audio_processing"))
        layout.addWidget(self.apply_audio_btn)
        
        layout.addStretch()
    
    def on_sample_rate_changed(self, text):
        self.custom_sample_rate_widget.setVisible(text == self.t("custom_sample_rate"))
    
    def on_bitrate_changed(self, text):
        self.custom_bitrate_widget.setVisible(text == self.t("custom_bitrate"))
    
    def retranslate_ui(self) -> None:
        self.audio_settings_group.setTitle(self.t("audio_settings"))
        self.audio_filters_group.setTitle(self.t("audio_filters"))
        self.apply_audio_btn.setText(self.t("apply_audio_processing"))
        
        # 更新采样率选项
        sample_rates = Config.DEFAULT_SAMPLE_RATES + [self.t("custom_sample_rate")]
        current_sr = self.sample_rate_combo.currentText()
        self.sample_rate_combo.clear()
        self.sample_rate_combo.addItems(sample_rates)
        if current_sr in sample_rates:
            self.sample_rate_combo.setCurrentText(current_sr)
        
        # 更新比特率选项
        bitrates = Config.DEFAULT_BITRATES + [self.t("custom_bitrate")]
        current_br = self.bitrate_combo.currentText()
        self.bitrate_combo.clear()
        self.bitrate_combo.addItems(bitrates)
        if current_br in bitrates:
            self.bitrate_combo.setCurrentText(current_br)


class AdvancedTab(BaseTabWidget):
    """高级功能标签页"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__(language_manager)
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 自定义参数
        self.custom_parameters_group = QGroupBox(self.t("custom_parameters"))
        custom_layout = QVBoxLayout(self.custom_parameters_group)
        
        custom_layout.addWidget(QLabel(self.t("ffmpeg_parameters")))
        self.custom_args_edit = QLineEdit()
        custom_layout.addWidget(self.custom_args_edit)
        
        custom_layout.addWidget(QLabel(self.t("example")))
        
        self.run_custom_btn = QPushButton(self.t("run_custom_command"))
        custom_layout.addWidget(self.run_custom_btn)
        
        layout.addWidget(self.custom_parameters_group)
        
        # 预设配置
        self.preset_configs_group = QGroupBox(self.t("preset_configs"))
        preset_layout = QVBoxLayout(self.preset_configs_group)
        
        self.preset_combo = QComboBox()
        presets = [self.t("no_preset"), self.t("high_quality_mp4"), self.t("high_quality_mp3"), 
                  self.t("web_optimized"), self.t("mobile_optimized")]
        self.preset_combo.addItems(presets)
        preset_layout.addWidget(self.preset_combo)
        
        layout.addWidget(self.preset_configs_group)
        
        layout.addStretch()
    
    def retranslate_ui(self) -> None:
        self.custom_parameters_group.setTitle(self.t("custom_parameters"))
        self.preset_configs_group.setTitle(self.t("preset_configs"))
        self.run_custom_btn.setText(self.t("run_custom_command"))
        
        # 更新预设选项
        presets = [self.t("no_preset"), self.t("high_quality_mp4"), self.t("high_quality_mp3"), 
                  self.t("web_optimized"), self.t("mobile_optimized")]
        current_preset = self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(presets)
        if current_preset in presets:
            self.preset_combo.setCurrentText(current_preset)


class SettingsTab(BaseTabWidget):
    """设置标签页"""
    
    def __init__(self, language_manager: LanguageManager, hardware_detector: HardwareDetector):
        super().__init__(language_manager)
        self.hardware_detector = hardware_detector
        self.setup_ui()
        self.update_hardware_info()  # 初始化时更新硬件信息
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # 语言设置
        self.language_settings_group = QGroupBox(self.t("language_settings"))
        language_layout = QGridLayout(self.language_settings_group)
        
        language_layout.addWidget(QLabel(self.t("language_settings")), 0, 0)
        self.language_combo = QComboBox()
        
        # 添加可用的语言选项
        available_languages = self.language_manager.get_available_languages()
        for lang_code in available_languages:
            display_name = self.language_manager.get_language_name(lang_code)
            self.language_combo.addItem(display_name, lang_code)

        # 设置默认语言为中文
        default_language_index = available_languages.index("zh_CN") if "zh_CN" in available_languages else 0
        self.language_combo.setCurrentIndex(default_language_index)

        language_layout.addWidget(self.language_combo, 0, 1)

        layout.addWidget(self.language_settings_group)
        
        # 硬件加速设置
        self.hardware_accel_settings_group = QGroupBox(self.t("hardware_accel_settings"))
        hardware_layout = QVBoxLayout(self.hardware_accel_settings_group)
        
        # 硬件加速状态
        hardware_status_layout = QHBoxLayout()
        hardware_status_layout.addWidget(QLabel(self.t("hardware_status") + ":"))
        self.hardware_status_label = QLabel(self.t("no_hardware_support"))
        hardware_status_layout.addWidget(self.hardware_status_label)
        hardware_status_layout.addStretch()
        hardware_layout.addLayout(hardware_status_layout)
        
        # 硬件加速器
        hwaccel_layout = QVBoxLayout()
        hwaccel_layout.addWidget(QLabel("支持的硬件加速器:"))
        self.hwaccel_text = QTextEdit()
        self.hwaccel_text.setMaximumHeight(80)
        self.hwaccel_text.setReadOnly(True)
        hwaccel_layout.addWidget(self.hwaccel_text)
        hardware_layout.addLayout(hwaccel_layout)
        
        # 硬件编码器
        encoder_layout = QVBoxLayout()
        encoder_layout.addWidget(QLabel("支持的硬件编码器:"))
        self.encoder_text = QTextEdit()
        self.encoder_text.setMaximumHeight(120)
        self.encoder_text.setReadOnly(True)
        encoder_layout.addWidget(self.encoder_text)
        hardware_layout.addLayout(encoder_layout)
        
        # 重新检测按钮
        self.detect_hardware_btn = QPushButton(self.t("re_detect"))
        hardware_layout.addWidget(self.detect_hardware_btn)
        
        layout.addWidget(self.hardware_accel_settings_group)
        
        # 版本信息
        self.version_info_group = QGroupBox(self.t("version_info"))
        version_layout = QVBoxLayout(self.version_info_group)
        
        self.current_version_label = QLabel(f"{self.t('current_version')} {Config.VERSION}")
        version_layout.addWidget(self.current_version_label)
        
        layout.addWidget(self.version_info_group)
        
        layout.addStretch()
    
    def update_hardware_info(self):
        """更新硬件信息显示"""
        self.hardware_status_label.setText(self.hardware_detector.get_hardware_status_text())
        self.hwaccel_text.setPlainText(self.hardware_detector.get_hardware_accel_text())
        self.encoder_text.setPlainText(self.hardware_detector.get_hardware_encoders_text())
    
    def retranslate_ui(self) -> None:
        self.language_settings_group.setTitle(self.t("language_settings"))
        self.hardware_accel_settings_group.setTitle(self.t("hardware_accel_settings"))
        self.version_info_group.setTitle(self.t("version_info"))
        
        self.detect_hardware_btn.setText(self.t("re_detect"))
        self.current_version_label.setText(f"{self.t('current_version')} {Config.VERSION}")
        
        # 更新语言下拉框的显示文本
        for i in range(self.language_combo.count()):
            lang_code = self.language_combo.itemData(i)
            display_name = self.language_manager.get_language_name(lang_code)
            self.language_combo.setItemText(i, display_name)
        
        # 更新硬件信息
        self.update_hardware_info()


class ProgressWidget(QWidget):
    """进度显示组件"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__()
        self.language_manager = language_manager
        self.current_language = "zh_CN"
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        self.progress_group = QGroupBox(self.t("progress"))
        progress_layout = QVBoxLayout(self.progress_group)
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        progress_info_layout = QHBoxLayout()
        self.progress_percent_label = QLabel("0%")
        progress_info_layout.addWidget(self.progress_percent_label)
        progress_info_layout.addStretch()
        self.estimated_time_label = QLabel(f"{self.t('estimated_time')}: --:--")
        progress_info_layout.addWidget(self.estimated_time_label)
        progress_layout.addLayout(progress_info_layout)
        
        self.processing_file_label = QLabel(f"{self.t('processing_file')}: ")
        progress_layout.addWidget(self.processing_file_label)
        
        self.waiting_label = QLabel("")
        self.waiting_label.setStyleSheet("color: blue; font-style: italic;")
        progress_layout.addWidget(self.waiting_label)
        
        layout.addWidget(self.progress_group)
    
    def t(self, key: str) -> str:
        return self.language_manager.get_text(self.current_language, key)
    
    def update_language(self, language: str) -> None:
        self.current_language = language
        self.retranslate_ui()
    
    def retranslate_ui(self) -> None:
        self.progress_group.setTitle(self.t("progress"))
        self.estimated_time_label.setText(f"{self.t('estimated_time')}: --:--")
        self.processing_file_label.setText(f"{self.t('processing_file')}: ")


class CommandPreviewWidget(QWidget):
    """命令预览组件"""
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__()
        self.language_manager = language_manager
        self.current_language = "zh_CN"
        self.setup_ui()
    
    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        self.command_preview_group = QGroupBox(self.t("command_preview"))
        command_layout = QVBoxLayout(self.command_preview_group)
        
        self.command_preview_text = QTextEdit()
        self.command_preview_text.setMaximumHeight(100)
        command_layout.addWidget(self.command_preview_text)
        
        action_layout = QHBoxLayout()
        self.update_preview_btn = QPushButton(self.t("update_preview"))
        action_layout.addWidget(self.update_preview_btn)
        
        self.process_btn = QPushButton(self.t("start_processing"))
        self.process_btn.setStyleSheet("font-weight: bold;")
        action_layout.addWidget(self.process_btn)
        action_layout.addStretch()
        
        command_layout.addLayout(action_layout)
        
        self.status_label = QLabel(self.t("ready"))
        command_layout.addWidget(self.status_label)
        
        layout.addWidget(self.command_preview_group)
    
    def t(self, key: str) -> str:
        return self.language_manager.get_text(self.current_language, key)
    
    def update_language(self, language: str) -> None:
        self.current_language = language
        self.retranslate_ui()
    
    def retranslate_ui(self) -> None:
        self.command_preview_group.setTitle(self.t("command_preview"))
        self.update_preview_btn.setText(self.t("update_preview"))
        self.process_btn.setText(self.t("start_processing"))
        self.status_label.setText(self.t("ready"))


class FFmpegGUI(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setup_encoding()
        
        self.language_manager = LanguageManager()
        self.current_language = "zh_CN"
        self.hardware_detector = HardwareDetector(self.language_manager)
        self.command_builder = FFmpegCommandBuilder(self.language_manager)
        
        self.input_file = ""
        self.output_file = ""
        self.is_processing = False
        self.ffmpeg_thread = None
        self.ffmpeg_available = False
        
        # 显示启动界面
        self.splash = SplashScreen(self.language_manager)
        self.splash.show()
        
        # 在后台线程中初始化
        self.initialization_complete = False
        self.init_thread = threading.Thread(target=self.initialize_app)
        self.init_thread.daemon = True
        self.init_thread.start()
        
        # 检查初始化状态
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_initialization)
        self.check_timer.start(100)

    def setup_encoding(self) -> None:
        """设置编码环境"""
        if sys.platform == 'win32':
            os.environ['PYTHONIOENCODING'] = 'utf-8'
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
                
    def initialize_app(self):
        """初始化应用程序"""
        try:
            # 更新启动界面状态
            self.splash.update_status("正在检查 FFmpeg...", "检测系统中是否安装FFmpeg")
            
            # 检查FFmpeg
            self.ffmpeg_available = self.detect_ffmpeg()
            
            if self.ffmpeg_available:
                # 更新启动界面状态
                self.splash.update_status("正在检测硬件加速支持...", "检测可用的硬件加速器")
                
                # 检测硬件加速
                self.splash.update_status("检测硬件加速器...", "CUDA, Quick Sync, VA-API等")
                self.hardware_detector.detect_hardware_acceleration()
                
                # 更新启动界面状态
                self.splash.update_status("检测硬件编码器...", "NVIDIA NVENC, Intel QSV, AMD AMF等")
                self.hardware_detector.detect_hardware_encoders()
                
                # 显示检测结果
                hwaccel_count = sum(1 for info in self.hardware_detector.hardware_acceleration.values() if info["supported"])
                encoder_count = sum(1 for info in self.hardware_detector.hardware_encoders.values() if info["supported"])
                self.splash.update_status("硬件检测完成", f"发现 {hwaccel_count} 个加速器, {encoder_count} 个编码器")
            else:
                self.splash.update_status("FFmpeg未安装", "跳过硬件检测...")
            
            # 更新启动界面状态
            self.splash.update_status("初始化完成", "启动主界面...")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"初始化过程中出现错误: {e}")
            import traceback
            traceback.print_exc()
            self.splash.update_status("初始化失败", str(e))
            time.sleep(2)
        finally:
            # 设置初始化完成标志
            self.initialization_complete = True

    
    def check_initialization(self):
        """检查初始化是否完成"""
        if self.initialization_complete:
            self.check_timer.stop()
            self.splash.close()
            self.init_ui()
            self.show()
    
    def t(self, key: str) -> str:
        return self.language_manager.get_text(self.current_language, key)
    
    def init_ui(self) -> None:
        self.setWindowTitle(self.t("title"))
        self.setGeometry(100, 100, 1280, 720)
        self.setMinimumSize(1024, 576)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #f0f0f0; }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                padding: 5px 10px;
                border: 1px solid #cccccc;
                border-radius: 3px;
                background-color: #f8f8f8;
            }
            QPushButton:hover { background-color: #e8e8e8; }
            QPushButton:pressed { background-color: #d8d8d8; }
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk { background-color: #4CAF50; }
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 3px;
                font-family: Consolas, monospace;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧面板
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 文件操作
        self.file_operations_tab = FileOperationsTab(self.language_manager)
        left_layout.addWidget(self.file_operations_tab)
        
        # 进度显示
        self.progress_widget = ProgressWidget(self.language_manager)
        left_layout.addWidget(self.progress_widget)
        
        # 命令预览
        self.command_preview_widget = CommandPreviewWidget(self.language_manager)
        left_layout.addWidget(self.command_preview_widget)
        
        # 右侧面板 - 标签页
        self.tab_widget = QTabWidget()
        
        # 格式转换标签页
        self.format_conversion_tab = FormatConversionTab(self.language_manager)
        self.tab_widget.addTab(self.format_conversion_tab, "🔄 " + self.t("format_conversion").replace("🔄 ", ""))
        
        # 视频处理标签页
        self.video_processing_tab = VideoProcessingTab(self.language_manager, self.hardware_detector)
        self.tab_widget.addTab(self.video_processing_tab, "🎬 " + self.t("video_encoding").replace("🎬 ", ""))
        
        # 音频处理标签页
        self.audio_processing_tab = AudioProcessingTab(self.language_manager)
        self.tab_widget.addTab(self.audio_processing_tab, "🎵 " + self.t("audio_settings").replace("🎵 ", ""))
        
        # 高级功能标签页
        self.advanced_tab = AdvancedTab(self.language_manager)
        self.tab_widget.addTab(self.advanced_tab, "🔧 " + self.t("custom_parameters").replace("🔧 ", ""))
        
        # 设置标签页
        self.settings_tab = SettingsTab(self.language_manager, self.hardware_detector)
        self.tab_widget.addTab(self.settings_tab, "⚙️ " + self.t("settings").replace("⚙️ ", ""))
        
        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(self.tab_widget, 1)
        
        self.connect_signals()
        self.update_tab_titles()
    
    def connect_signals(self) -> None:
        # 文件操作
        self.file_operations_tab.input_browse_btn.clicked.connect(self.browse_input_file)
        self.file_operations_tab.output_browse_btn.clicked.connect(self.browse_output_file)
        self.file_operations_tab.input_file_edit.textChanged.connect(self.on_input_file_changed)
        
        # 格式转换
        self.format_conversion_tab.convert_btn.clicked.connect(self.convert_format)
        self.format_conversion_tab.ncm_to_mp3_btn.clicked.connect(self.quick_ncm_to_mp3)
        self.format_conversion_tab.extract_audio_btn.clicked.connect(self.extract_audio)
        self.format_conversion_tab.extract_video_btn.clicked.connect(self.extract_video)
        self.format_conversion_tab.compress_media_btn.clicked.connect(self.compress_media)
        
        # 视频处理
        self.video_processing_tab.apply_video_btn.clicked.connect(self.apply_video_processing)
        
        # 音频处理
        self.audio_processing_tab.apply_audio_btn.clicked.connect(self.apply_audio_processing)
        
        # 高级功能
        self.advanced_tab.run_custom_btn.clicked.connect(self.run_custom_command)
        self.advanced_tab.preset_combo.currentTextChanged.connect(self.apply_preset)
        
        # 设置
        self.settings_tab.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.settings_tab.detect_hardware_btn.clicked.connect(self.redetect_hardware_acceleration)
        
        # 命令预览
        self.command_preview_widget.update_preview_btn.clicked.connect(self.update_preview)
        self.command_preview_widget.process_btn.clicked.connect(self.start_processing)
    
    def update_tab_titles(self):
        """更新标签页标题"""
        tab_titles = [
            "🔄 " + self.t("format_conversion").replace("🔄 ", ""),
            "🎬 " + self.t("video_encoding").replace("🎬 ", ""),
            "🎵 " + self.t("audio_settings").replace("🎵 ", ""),
            "🔧 " + self.t("custom_parameters").replace("🔧 ", ""),
            "⚙️ " + self.t("settings").replace("⚙️ ", "")
        ]
        
        for i, title in enumerate(tab_titles):
            if i < self.tab_widget.count():
                self.tab_widget.setTabText(i, title)
    
    def on_language_changed(self, index):
        """语言切换"""
        if index >= 0:
            new_language = self.settings_tab.language_combo.itemData(index)
            if new_language != self.current_language:
                self.switch_language(new_language)
    
    def switch_language(self, language):
        """切换语言"""
        if self.current_language == language:
            return
        
        self.command_preview_widget.status_label.setText(self.t("language_switching"))
        QApplication.processEvents()
        
        self.current_language = language
        
        # 更新所有组件的语言
        self.setWindowTitle(self.t("title"))
        
        self.file_operations_tab.update_language(language)
        self.format_conversion_tab.update_language(language)
        self.video_processing_tab.update_language(language)
        self.audio_processing_tab.update_language(language)
        self.advanced_tab.update_language(language)
        self.settings_tab.update_language(language)
        self.progress_widget.update_language(language)
        self.command_preview_widget.update_language(language)
        
        self.update_tab_titles()
        
        self.command_preview_widget.status_label.setText(self.t("ready"))
    
    def browse_input_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.t("source_file"),
            "",
            f"视频文件 ({Config.SUPPORTED_VIDEO_FORMATS});;"
            f"音频文件 ({Config.SUPPORTED_AUDIO_FORMATS});;"
            f"所有文件 (*.*)"
        )
        if filename:
            self.file_operations_tab.input_file_edit.setText(filename)
    
    def browse_output_file(self) -> None:
        default_ext = "." + self.format_conversion_tab.format_combo.currentText()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            self.t("output_file"),
            "",
            f"MP4文件 (*.mp4);;AVI文件 (*.avi);;MOV文件 (*.mov);;"
            f"MKV文件 (*.mkv);;MP3文件 (*.mp3);;WAV文件 (*.wav);;"
            f"所有文件 (*.*)"
        )
        if filename:
            self.file_operations_tab.output_file_edit.setText(filename)
    
    def on_input_file_changed(self, text: str) -> None:
        self.input_file = text
        if text and not self.file_operations_tab.output_file_edit.text():
            base, ext = os.path.splitext(text)
            output_ext = "." + self.format_conversion_tab.format_combo.currentText()
            self.file_operations_tab.output_file_edit.setText(f"{base}_converted{output_ext}")
        
        if text:
            info = FileProcessor.get_file_info(text)
            self.file_operations_tab.file_info_text.setPlainText(info)
    
    def convert_format(self) -> None:
        input_file = self.file_operations_tab.input_file_edit.text()
        if not input_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_file"))
            return
        
        # NCM转MP3特殊处理
        if self.format_conversion_tab.format_combo.currentText() == "ncm_to_mp3":
            if not input_file.lower().endswith('.ncm'):
                QMessageBox.warning(self, self.t("warning"), "NCM转MP3功能只能处理.ncm文件")
                return
            
            if not self.file_operations_tab.output_file_edit.text():
                base, _ = os.path.splitext(input_file)
                self.file_operations_tab.output_file_edit.setText(base + ".mp3")
            
            self.convert_ncm_to_mp3()
            return
        
        # 普通格式转换
        if self.file_operations_tab.output_file_edit.text():
            base, _ = os.path.splitext(self.file_operations_tab.output_file_edit.text())
            new_output = base + "." + self.format_conversion_tab.format_combo.currentText()
            self.file_operations_tab.output_file_edit.setText(new_output)
        
        self.start_processing()
    
    def convert_ncm_to_mp3(self) -> None:
        try:
            input_file = self.file_operations_tab.input_file_edit.text()
            output_file = self.file_operations_tab.output_file_edit.text()
            
            self.command_preview_widget.status_label.setText(self.t("decrypting_ncm"))
            self.progress_widget.progress_bar.setValue(10)
            QApplication.processEvents()
            
            # 解密NCM文件
            decrypted_file = NCMDecoder.decrypt_ncm_file(input_file)
            
            if not decrypted_file or not os.path.exists(decrypted_file):
                raise Exception("解密失败")
            
            self.progress_widget.progress_bar.setValue(50)
            self.command_preview_widget.status_label.setText(self.t("converting_to_mp3"))
            QApplication.processEvents()
            
            # 转换为MP3
            cmd = [
                "ffmpeg", "-i", decrypted_file,
                "-codec:a", "libmp3lame",
                "-q:a", "2",
                "-y", output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=True
            )
            
            # 清理临时文件
            try:
                os.remove(decrypted_file)
            except:
                pass
            
            self.progress_widget.progress_bar.setValue(100)
            self.command_preview_widget.status_label.setText(self.t("ncm_conversion_complete"))
            QMessageBox.information(self, self.t("success"),
                                  f"{self.t('ncm_conversion_complete')}:\n{output_file}")
            
        except subprocess.CalledProcessError as e:
            self.command_preview_widget.status_label.setText(self.t("failed"))
            QMessageBox.critical(self, self.t("error"),
                               f"FFmpeg转换失败:\n{e.stderr if e.stderr else '未知错误'}")
        except Exception as e:
            self.command_preview_widget.status_label.setText(self.t("failed"))
            QMessageBox.critical(self, self.t("error"),
                               f"{self.t('ncm_decryption_failed')}:\n{str(e)}")
        finally:
            self.command_preview_widget.process_btn.setText(self.t("start_processing"))
            self.is_processing = False
    
    def quick_ncm_to_mp3(self) -> None:
        input_file = self.file_operations_tab.input_file_edit.text()
        if not input_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_file"))
            return
        
        if not input_file.lower().endswith('.ncm'):
            QMessageBox.warning(self, self.t("warning"), "请选择.ncm文件")
            return
        
        base, _ = os.path.splitext(input_file)
        output_file = base + ".mp3"
        self.file_operations_tab.output_file_edit.setText(output_file)
        self.format_conversion_tab.format_combo.setCurrentText("ncm_to_mp3")
        self.convert_ncm_to_mp3()
    
    def extract_audio(self) -> None:
        input_file = self.file_operations_tab.input_file_edit.text()
        if not input_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_file"))
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("extract_audio"),
            "",
            "MP3文件 (*.mp3);;WAV文件 (*.wav);;所有文件 (*.*)"
        )
        
        if output_path:
            self.file_operations_tab.output_file_edit.setText(output_path)
            cmd = ["ffmpeg", "-i", input_file, "-vn", "-c:a", "mp3", "-b:a", "192k", "-y", output_path]
            self.run_ffmpeg_command_direct(cmd)
    
    def extract_video(self) -> None:
        input_file = self.file_operations_tab.input_file_edit.text()
        if not input_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_file"))
            return
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            self.t("extract_video"),
            "",
            "MP4文件 (*.mp4);;所有文件 (*.*)"
        )
        
        if output_path:
            self.file_operations_tab.output_file_edit.setText(output_path)
            cmd = ["ffmpeg", "-i", input_file, "-an", "-c:v", "copy", "-y", output_path]
            self.run_ffmpeg_command_direct(cmd)
    
    def compress_media(self) -> None:
        self.format_conversion_tab.video_quality_combo.setCurrentText(self.t("medium_quality"))
        self.format_conversion_tab.audio_quality_combo.setCurrentText(self.t("medium_quality"))
        self.start_processing()
    
    def apply_video_processing(self) -> None:
        self.start_processing()
    
    def apply_audio_processing(self) -> None:
        self.start_processing()
    
    def run_custom_command(self) -> None:
        self.start_processing()
    
    def apply_preset(self, preset):
        """应用预设配置"""
        if preset == self.t("high_quality_mp4"):
            self.format_conversion_tab.format_combo.setCurrentText("mp4")
            self.video_processing_tab.video_codec_combo.setCurrentText("libx264")
            self.audio_processing_tab.audio_codec_combo.setCurrentText("aac")
            self.format_conversion_tab.video_quality_combo.setCurrentText(self.t("high_quality"))
            self.format_conversion_tab.audio_quality_combo.setCurrentText(self.t("high_quality"))
        elif preset == self.t("high_quality_mp3"):
            self.format_conversion_tab.format_combo.setCurrentText("mp3")
            self.audio_processing_tab.audio_codec_combo.setCurrentText("libmp3lame")
            self.audio_processing_tab.bitrate_combo.setCurrentText("320k")
        elif preset == self.t("web_optimized"):
            self.format_conversion_tab.format_combo.setCurrentText("mp4")
            self.video_processing_tab.video_codec_combo.setCurrentText("libx264")
            self.audio_processing_tab.audio_codec_combo.setCurrentText("aac")
            self.video_processing_tab.resolution_combo.setCurrentText("1280x720")
            self.format_conversion_tab.video_quality_combo.setCurrentText(self.t("medium_quality"))
        elif preset == self.t("mobile_optimized"):
            self.format_conversion_tab.format_combo.setCurrentText("mp4")
            self.video_processing_tab.video_codec_combo.setCurrentText("libx264")
            self.audio_processing_tab.audio_codec_combo.setCurrentText("aac")
            self.video_processing_tab.resolution_combo.setCurrentText("854x480")
            self.format_conversion_tab.video_quality_combo.setCurrentText(self.t("medium_quality"))
    
    def build_ffmpeg_command(self) -> Optional[List[str]]:
        input_file = self.file_operations_tab.input_file_edit.text()
        output_file = self.file_operations_tab.output_file_edit.text()
        
        if not input_file or not output_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_output"))
            return None
        
        params = {
            "input_file": input_file,
            "output_file": output_file,
            "video_codec": self.video_processing_tab.video_codec_combo.currentText(),
            "audio_codec": self.audio_processing_tab.audio_codec_combo.currentText(),
            "resolution": self.video_processing_tab.resolution_combo.currentText(),
            "custom_resolution": self.video_processing_tab.custom_resolution_edit.text(),
            "fps": self.video_processing_tab.fps_combo.currentText(),
            "custom_fps": self.video_processing_tab.custom_fps_edit.text(),
            "sample_rate": self.audio_processing_tab.sample_rate_combo.currentText(),
            "custom_sample_rate": self.audio_processing_tab.custom_sample_rate_edit.text(),
            "channels": self.audio_processing_tab.channels_combo.currentText(),
            "bitrate": self.audio_processing_tab.bitrate_combo.currentText(),
            "custom_bitrate": self.audio_processing_tab.custom_bitrate_edit.text(),
            "video_quality": self.format_conversion_tab.video_quality_combo.currentText(),
            "hwaccel": self.video_processing_tab.hwaccel_combo.currentText(),  # 添加硬件加速器参数
            "crop_enabled": self.video_processing_tab.crop_check.isChecked(),
            "crop_params": self.video_processing_tab.crop_params_edit.text(),
            "scale_enabled": self.video_processing_tab.scale_check.isChecked(),
            "rotate_enabled": self.video_processing_tab.rotate_check.isChecked(),
            "rotate_angle": self.video_processing_tab.rotate_angle_combo.currentText(),
            "volume_enabled": self.audio_processing_tab.volume_check.isChecked(),
            "volume_factor": self.audio_processing_tab.volume_factor_edit.text(),
            "custom_args": self.advanced_tab.custom_args_edit.text()
        }
        
        return self.command_builder.build_command(params)
    
    def update_preview(self) -> None:
        cmd = self.build_ffmpeg_command()
        if cmd:
            self.command_preview_widget.command_preview_text.setPlainText(" ".join(cmd))
    
    def start_processing(self) -> None:
        if self.is_processing:
            return
        
        input_file = self.file_operations_tab.input_file_edit.text()
        output_file = self.file_operations_tab.output_file_edit.text()
        
        if not input_file or not output_file:
            QMessageBox.critical(self, self.t("error"), self.t("select_input_output"))
            return
        
        cmd = self.build_ffmpeg_command()
        if not cmd:
            return
        
        self.is_processing = True
        self.command_preview_widget.process_btn.setText(self.t("processing"))
        self.command_preview_widget.status_label.setText(self.t("processing"))
        self.progress_widget.progress_bar.setValue(0)
        
        self.ffmpeg_thread = FFmpegWorker(cmd)
        self.ffmpeg_thread.progress_updated.connect(self.update_progress)
        self.ffmpeg_thread.status_updated.connect(self.update_status)
        self.ffmpeg_thread.finished_signal.connect(self.on_processing_finished)
        self.ffmpeg_thread.start()
        
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.simulate_progress)
        self.progress_timer.start(500)
    
    def simulate_progress(self) -> None:
        if not self.is_processing:
            self.progress_timer.stop()
            return
        
        current_value = self.progress_widget.progress_bar.value()
        if current_value < 90:
            new_value = min(current_value + 5, 90)
            self.progress_widget.progress_bar.setValue(new_value)
    
    def update_progress(self, value: int) -> None:
        self.progress_widget.progress_bar.setValue(value)
    
    def update_status(self, status: str) -> None:
        self.command_preview_widget.status_label.setText(status)
    
    def on_processing_finished(self, success: bool, message: str) -> None:
        self.is_processing = False
        self.command_preview_widget.process_btn.setText(self.t("start_processing"))
        self.progress_widget.progress_bar.setValue(100 if success else 0)
        
        if success:
            self.command_preview_widget.status_label.setText(self.t("completed"))
            QMessageBox.information(self, self.t("success"), self.t("completed"))
        else:
            self.command_preview_widget.status_label.setText(self.t("failed"))
            QMessageBox.critical(self, self.t("error"), message)
    
    def run_ffmpeg_command_direct(self, cmd: List[str]) -> None:
        self.is_processing = True
        self.command_preview_widget.process_btn.setText(self.t("processing"))
        self.command_preview_widget.status_label.setText(self.t("processing"))
        self.progress_widget.progress_bar.setValue(0)
        
        self.ffmpeg_thread = FFmpegWorker(cmd)
        self.ffmpeg_thread.progress_updated.connect(self.update_progress)
        self.ffmpeg_thread.status_updated.connect(self.update_status)
        self.ffmpeg_thread.finished_signal.connect(self.on_processing_finished)
        self.ffmpeg_thread.start()
        
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.simulate_progress)
        self.progress_timer.start(500)
    
    def detect_ffmpeg(self) -> bool:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                check=True
            )
            version = result.stdout.split('\n')[0]
            print(f"FFmpeg版本: {version}")
            return True
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.show_installation_guide()
            return False
    
    def redetect_hardware_acceleration(self):
        """重新检测硬件加速"""
        self.hardware_detector.detect_all()
        self.settings_tab.update_hardware_info()
        
        # 更新视频编码器选项
        codecs = self.hardware_detector.get_supported_video_codecs()
        current_codec = self.video_processing_tab.video_codec_combo.currentText()
        self.video_processing_tab.video_codec_combo.clear()
        self.video_processing_tab.video_codec_combo.addItems(codecs)
        if current_codec in codecs:
            self.video_processing_tab.video_codec_combo.setCurrentText(current_codec)
        
        # 更新硬件加速选项
        hwaccel_options = self.hardware_detector.get_hwaccel_options()
        current_hwaccel = self.video_processing_tab.hwaccel_combo.currentText()
        self.video_processing_tab.hwaccel_combo.clear()
        self.video_processing_tab.hwaccel_combo.addItems(hwaccel_options)
        if current_hwaccel in hwaccel_options:
            self.video_processing_tab.hwaccel_combo.setCurrentText(current_hwaccel)
        
        QMessageBox.information(self, self.t("detection_completed"), self.t("hardware_support_detected"))
    
    def show_installation_guide(self) -> None:
        install_dialog = QDialog(self)
        install_dialog.setWindowTitle(self.t("ffmpeg_not_found"))
        install_dialog.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout(install_dialog)
        
        title = QLabel(self.t("installation_guide"))
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        guide_text = QTextEdit()
        guide_text.setPlainText("""
        FFmpeg 未安装或未在系统PATH中找到。
        
        Windows系统:
        1. 访问 https://ffmpeg.org/download.html
        2. 下载Windows版本压缩包
        3. 解压到 C:\\ffmpeg 目录
        4. 将 C:\\ffmpeg\\bin 添加到系统PATH环境变量
        5. 重新启动命令提示符并验证安装: ffmpeg -version
        
        macOS系统:
        1. 使用Homebrew安装: brew install ffmpeg
        
        Linux系统:
        1. Ubuntu/Debian: sudo apt install ffmpeg
        2. CentOS/RHEL: sudo yum install ffmpeg
        3. Arch Linux: sudo pacman -S ffmpeg
        
        验证安装: 在终端运行 ffmpeg -version
        """)
        guide_text.setReadOnly(True)
        layout.addWidget(guide_text)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(install_dialog.close)
        layout.addWidget(close_btn)
        
        install_dialog.exec_()


def main():
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("FFmpeg GUI")
        app.setApplicationVersion(Config.VERSION)
        
        window = FFmpegGUI()
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()
        
        error_msg = QMessageBox()
        error_msg.setIcon(QMessageBox.Critical)
        error_msg.setWindowTitle("启动错误")
        error_msg.setText(f"程序启动时发生错误:\n{str(e)}")
        error_msg.exec_()


if __name__ == "__main__":
    main()