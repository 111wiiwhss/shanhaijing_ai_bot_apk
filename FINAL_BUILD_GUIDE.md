# 山海经异变AI代练 - 最终构建指南

## 构建方法概述

由于GitHub Actions中Docker构建遇到权限问题，我们提供了两种构建方案：

### 方案一：使用Docker构建（带详细调试）
- **文件**：`.github/workflows/build-apk.yml`
- **特点**：使用Docker容器，隔离环境，详细调试信息
- **适用场景**：希望使用隔离环境构建，需要详细日志

### 方案二：直接环境构建（推荐）
- **文件**：`.github/workflows/build-apk-simple.yml`
- **特点**：直接在GitHub Actions环境中安装依赖，跳过Docker
- **适用场景**：避免Docker权限问题，更快的构建速度

## GitHub Actions构建步骤

### 方法一：使用Docker构建

1. 访问GitHub仓库：https://github.com/111wiiwhss/shanhaijing_ai_bot_apk
2. 点击顶部的"Actions"标签
3. 在左侧工作流列表中选择"Build Android APK"
4. 点击"Run workflow"按钮
5. 在弹出的对话框中点击"Run workflow"确认
6. 等待构建完成（约60-120分钟）
7. 构建完成后，在"Artifacts"部分下载APK文件

### 方法二：直接环境构建（推荐）

1. 访问GitHub仓库：https://github.com/111wiiwhss/shanhaijing_ai_bot_apk
2. 点击顶部的"Actions"标签
3. 在左侧工作流列表中选择"Build Android APK (Simple)"
4. 点击"Run workflow"按钮
5. 在弹出的对话框中点击"Run workflow"确认
6. 等待构建完成（约60-180分钟）
7. 构建完成后，在"Artifacts"部分下载APK文件

## Windows本地构建步骤

### 使用PowerShell脚本

1. 安装Docker Desktop：https://www.docker.com/products/docker-desktop
2. 启用Docker Desktop的WSL2后端
3. 克隆GitHub仓库：
   ```powershell
   git clone https://github.com/111wiiwhss/shanhaijing_ai_bot_apk
   cd shanhaijing_ai_bot_apk
   ```
4. 运行构建脚本：
   ```powershell
   .\build_apk_windows.ps1
   ```
5. 构建完成后，APK文件将输出到`output`目录

### 直接使用Buildozer（高级用户）

1. 安装Python 3.10或更高版本
2. 安装系统依赖：
   ```powershell
   choco install -y python310 git curl unzip openjdk17
   ```
3. 安装Python依赖：
   ```powershell
   pip install buildozer cython numpy kivy
   ```
4. 运行构建：
   ```powershell
   buildozer android debug
   ```

## 构建常见问题及解决方案

### 问题1：Docker构建失败，错误代码125
**解决方案**：尝试使用"Build Android APK (Simple)"工作流，跳过Docker直接构建

### 问题2：构建时间过长
**解决方案**：
- 构建过程正常需要60-180分钟
- 可以在构建日志中查看实时进度
- 如果超过2小时仍未完成，可取消构建并尝试其他方法

### 问题3：构建成功但没有APK文件
**解决方案**：
- 检查构建日志，查看是否有编译错误
- 尝试使用简化的构建规格
- 检查bin目录是否生成了APK文件

### 问题4：Android SDK安装失败
**解决方案**：
- 使用"Build Android APK (Simple)"工作流，自动安装SDK
- 确保网络连接正常，GitHub Actions可访问Google服务器

## 构建产物说明

- **APK文件**：构建完成后生成的Android安装包
- **构建日志**：包含详细的构建过程和错误信息
- **调试信息**：帮助分析构建失败原因

## 构建成功后使用说明

1. 将APK文件传输到Android设备
2. 在设备上启用"未知来源应用安装"选项
3. 点击APK文件进行安装
4. 安装完成后，打开"山海经异变AI代练"应用
5. 按照应用内提示进行设置
6. 启动AI代练功能

## 技术支持

如果遇到构建问题，可以：
1. 查看GitHub Actions构建日志
2. 检查FINAL_BUILD_GUIDE.md文档
3. 参考项目README.md
4. 在GitHub仓库提交Issue

## 项目链接

- GitHub仓库：https://github.com/111wiiwhss/shanhaijing_ai_bot_apk
- 构建状态：https://github.com/111wiiwhss/shanhaijing_ai_bot_apk/actions

---

**构建建议**：首次构建推荐使用"Build Android APK (Simple)"工作流，避免Docker相关问题。如果构建成功，可以尝试使用Docker工作流进行后续构建。

**构建时间**：首次构建由于需要下载依赖，时间较长；后续构建会有缓存，时间会缩短。

**设备支持**：构建生成的APK支持Android 5.0及以上版本，支持ARM64架构设备。
