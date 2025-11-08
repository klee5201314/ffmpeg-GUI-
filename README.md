# ffmpeg-GUI-
ffmpeg GUI一款基于 Python 与 Tkinter 开发的图形化 FFmpeg 媒体处理工具，旨在为不熟悉命令行操作的用户提供简单、直观、功能强大的音视频处理体验。无论你是想转换格式、提取音视频、压缩文件，还是进行高级的编解码与滤镜处理，该程序都能帮你轻松完成。

# 使用前请安装ffmpeg
# 1. FFmpeg 官方网站
```bash
https://ffmpeg.org/download.html
```
# 2. Windows 预编译版本
BtbN/FFmpeg-Builds (推荐)
```bash
https://github.com/BtbN/FFmpeg-Builds/releases
```
Gyan.dev (推荐)
```bash
https://www.gyan.dev/ffmpeg/builds/
```
Windows Essentials 版本
```bash
https://github.com/essential-overlay/ffmpeg-essentials/releases
```
# 3. macOS 版本
Homebrew
```bash
brew install ffmpeg
```
```text
https://formulae.brew.sh/formula/ffmpeg
```
MacPorts
```bash
sudo port install ffmpeg
```
# 4. Linux 版本
各发行版包管理器

Ubuntu/Debian
```bash
sudo apt update && sudo apt install ffmpeg
```
CentOS/RHEL/Fedora
```bash
sudo dnf install ffmpeg
```
或
```bash
sudo yum install ffmpeg
Arch Linux
sudo pacman -S ffmpeg
```
静态编译版本
```text
https://johnvansickle.com/ffmpeg/
```

# 📥 安装指南（Windows 用户）
简易安装步骤：
访问 
```txt
https://github.com/BtbN/FFmpeg-Builds/releases
```
下载最新版本的 ffmpeg-master-latest-win64-gpl.zip

解压到 C:\ffmpeg

将 C:\ffmpeg\bin 添加到系统 PATH 环境变量

重新打开命令提示符，输入 ffmpeg -version 验证

验证安装：
```cmd
ffmpeg -version
```
🔧 其他资源
FFmpeg 文档
```text
https://ffmpeg.org/documentation.html
```
FFmpeg Wiki
```text
https://trac.ffmpeg.org/wiki
```
在线 FFmpeg 命令生成器
```text
https://ffmpeg.guide/
```



# 特色功能:
🚀 硬件加速支持
自动检测并支持 NVIDIA CUDA、Intel Quick Sync、AMD AMF、Apple VideoToolbox 等硬件编解码器

动态加载可用的硬件编码器，提升处理速度

🔄 多格式转换
支持常见视频格式：MP4、AVI、MOV、MKV、WebM 等

支持常见音频格式：MP3、WAV、FLAC、AAC、M4A 等

支持 NCM 加密音频文件转 MP3（内置解密 + ncmdump 支持）

🎛️ 模块化操作界面
基础转换：快速选择输出格式与质量

视频处理：编码器选择、分辨率、帧率、裁剪、旋转、缩放

音频处理：编码器、采样率、声道、音量调整

高级自定义：支持原生 FFmpeg 参数输入

预设配置：一键应用高质量 MP4、MP3、网页优化等方案

🌐 多语言支持
内置简体中文与英文界面

可实时切换语言，适应不同用户群体

📊 实时进度与状态显示
动态进度条与百分比显示

预估剩余时间

处理完成自动提示

技术架构
前端：Tkinter + ttk 组件

后端：FFmpeg 命令行调用 + 子进程管理

硬件检测：动态解析 ffmpeg -hwaccels 与 ffmpeg -encoders

NCM 解密：集成 ncmdump 库与内置备用解密算法

多线程处理：防止界面卡顿，支持任务中断

适用人群
视频创作者、自媒体人

音频处理爱好者

需要批量处理媒体文件的用户

不想记忆复杂 FFmpeg 命令的普通用户

使用说明
选择输入文件（支持拖拽或浏览）

设置输出路径与格式

根据需要调整参数（如编码器、分辨率、滤镜等）

预览 FFmpeg 命令（可选）

点击“开始处理”，等待完成即可

未来展望
我将持续迭代，未来计划支持：

批量文件处理

更多音视频滤镜

流媒体录制与转码

插件化架构，支持用户自定义脚本

# 如果你正在寻找一个既强大又易用的本地音视频处理工具，不妨试试我 —— 一个懂你的 FFmpeg 图形化助手。

🎉 让媒体处理，简单如点击。
