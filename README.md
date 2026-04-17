# cross_circle

基于纯 Python（PIL + NumPy）实现的智能车赛道二值化、透视变换与十字/圆环元素识别系统，完全不依赖 OpenCV。

## ✨ 功能模块

| 模块 | 功能描述 | 对应文件 |
|------|----------|----------|
| **赛道图像生成** | 生成直道、十字路口、圆环赛道三种二值化俯视图 | `generate.py` |
| **透视变换** | 模拟摄像头倾斜拍摄效果（正向）与逆透视恢复（逆向） | `apply_perspective.py` & `Inverse_transformation.py` |
| **元素识别** | 检测二值化图像中的十字路口和圆环入口 | `what.py` |

## 📁 项目结构
```
cross_circle/
├── generate.py # 生成平视二值赛道图（直道/十字/圆环）
├── apply_perspective.py # 正向透视变换，模拟倾斜拍摄
├── Inverse_transformation.py # 逆透视变换，从透视图中估计并恢复俯视图
├── main.py # 集成入口，一键运行完整流程
├── what.py # 赛道元素识别（十字/圆环检测）
├── pic/ # 生成的示例图像
│ ├── track_normal.png
│ ├── track_cross.png
│ ├── track_roundabout.png
│ └── *_perspective.png # 透视变换后的图像
├── .gitignore # Git 忽略配置（排除 .venv, pycache 等）
└── README.md # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备
```
- Python 3.7+
- 安装依赖：
```
```bash
pip install pillow numpy
```
### 2. 一键运行完整流程
```bash
python main.py
```
该脚本会按顺序执行以下步骤：
```
调用 generate.py 生成直道、十字、圆环三种赛道的俯视图。

调用 apply_perspective.py 对生成的俯视图进行正向透视变换，模拟倾斜拍摄。

调用 Inverse_transformation.py 从生成的透视图中，通过检测赛道边线自动估计逆透视矩阵，并尝试恢复俯视图。
```
### 3. 分步运行与自定义

你也可以单独运行各个模块进行调试或自定义生成赛道图像：

```bash
python generate.py
```
可在 generate_all_test_images 函数中调整图像尺寸 (w, h) 和赛道参数 (track_width, ring_radius)

应用透视变换：
```bash
python apply_perspective.py
```
可在 batch_transform_all 函数中修改 change 参数来控制透视的倾斜程度。 

逆透视变换：
```bash
python Inverse_transformation.py
```
该模块会自动从透视图中检测赛道边线，计算逆透视矩阵并恢复俯视图。

运行元素识别：
```python
from what import TrackElementDetector
```

# 对任意二值化赛道图像进行识别

## 🔧 核心模块详解
### 1. 赛道生成 (generate.py)
```
draw_straight_track(): 绘制垂直直道。

draw_cross_track(): 绘制十字路口（纵向主道 + 横向横道）。

draw_roundabout_track(): 绘制圆环赛道，内圆（障碍物）与直道右侧相切，符合真实场景。
```
### 2. 透视变换 (apply_perspective.py & Inverse_transformation.py)
```
正向变换 (apply_perspective.py): 
通过指定原图四个角在输出图像中的目标位置，计算单应矩阵并应用透视变换，模拟倾斜拍摄。

逆向变换 (Inverse_transformation.py): 
从透视图像中自动提取赛道左右边线，基于“真实世界赛道等宽”的假设，估算逆透视矩阵，实现无需标定的俯视图恢复。
```
### 3. 元素识别 (what.py)
```
十字识别: 
通过检测赛道左右边线的“拐点”（斜率突变点）数量和分布，结合中心区域白色占比来判定。

圆环识别: 
通过分析图像下半部分中心列的黑色连通宽度，并检查两侧是否有白色赛道来判定。
```
### 📄 许可证
本项目采用 MIT 许可证，详情请见 LICENSE 文件。

### 🙏 致谢
本项目为智能车竞赛视觉组的基础模块实现，适用于学习透视变换原理和传统图像处理算法。