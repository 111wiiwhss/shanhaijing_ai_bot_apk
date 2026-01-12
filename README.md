# 山海经异变AI代练系统

一个基于AI的山海经异变游戏代练系统，可以自动完成游戏中的各种任务。

## 功能特性

- 自动识别游戏界面
- 智能决策和操作
- 支持多种游戏场景
- 可在Android设备上运行

## 构建方法

### 方法一：使用GitHub Actions

1. Fork此仓库
2. 在Actions页面触发构建
3. 下载生成的APK文件

### 方法二：使用Docker本地构建

```bash
docker-compose -f docker-compose.apk.yml up
```

### 方法三：本地直接构建

```bash
pip install -r requirements.txt
buildozer android debug
```

## 技术栈

- Python
- Kivy (UI框架)
- OpenCV (图像识别)
- TensorFlow (AI模型)
- Buildozer (APK打包)
- Docker (容器化)

## 项目结构

```
├── kivy_app/             # Kivy应用代码
│   ├── main.py           # 主程序入口
│   └── buildozer.spec    # Buildozer配置
├── bot/                  # 游戏机器人逻辑
├── models/               # AI模型
├── config/               # 配置文件
└── buildozer.spec        # 主Buildozer配置
```

## 使用说明

1. 将生成的APK安装到Android设备
2. 打开游戏并进入主界面
3. 启动AI代练应用
4. 按照提示进行设置
5. 开始自动代练

## 注意事项

- 请遵守游戏规则，合理使用AI代练
- 使用过程中请保持设备电量充足
- 首次使用可能需要一定的初始化时间
- 建议在稳定网络环境下使用

## 许可证

MIT License
