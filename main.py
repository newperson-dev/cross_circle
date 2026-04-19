"""
智能车赛道测试数据生成、透视变换与元素识别集成脚本。
依次执行：
1. 生成平视二值图 (generate.py)
2. 施加倾斜透视变换 (apply_perspective.py)
3. 逆透视变换恢复俯视图 (Inverse_transformation.py)
4. 对生成的图像进行十字和圆环检测 (what.py)
"""

import subprocess
import sys
from generate import generate_all_test_images
from apply_perspective import batch_transform_all
from Inverse_transformation import inverse_transform_image
from what import TrackElementDetector


def detect_on_image(image_path, description=""):
    """对指定图像进行赛道元素检测并输出结果"""
    print(f"\n🔍 检测图像: {image_path} {description}")
    try:
        detector = TrackElementDetector(image_path)
        detector.run()
    except Exception as e:
        print(f"❌ 检测失败: {e}")


if __name__ == "__main__":
    # 参数设置
    w, h = 1280, 960
    track_width = 100
    r_c_y = h * (3/10)
    ring_radius = 200
    change = 0.3

    # 第一步：生成原始平视图
    print("=" * 50)
    print("第一步：生成赛道俯视图")
    print("=" * 50)
    generate_all_test_images(w, h, track_width, r_c_y, ring_radius)

    # 第二步：应用透视变换（模拟倾斜拍摄）
    print("\n" + "=" * 50)
    print("第二步：正向透视变换")
    print("=" * 50)
    batch_transform_all(w, h, change)

    # 第三步：逆透视变换恢复俯视图（针对圆环和十字，可扩展）
    print("\n" + "=" * 50)
    print("第三步：逆透视变换")
    print("=" * 50)
    # 对圆环图像进行逆变换
    inverse_transform_image(
        input_path="pic/track_roundabout_perspective.png",
        output_path="pic/track_roundabout_inver.png",
        output_size=(w, h)
    )
    # 对十字图像进行逆变换（可选，若需要恢复十字俯视图）
    inverse_transform_image(
        input_path="pic/track_cross_perspective.png",
        output_path="pic/track_cross_inver.png",
        output_size=(w, h)
    )

    # 第四步：赛道元素识别
    print("\n" + "=" * 50)
    print("第四步：赛道元素识别")
    print("=" * 50)

    # 检测原始俯视图（生成后未变换）
    detect_on_image("pic/track_cross.png", "(俯视图-十字)")
    detect_on_image("pic/track_roundabout.png", "(俯视图-圆环)")

    # 检测透视图像（模拟摄像头拍摄）
    detect_on_image("pic/track_cross_perspective.png", "(透视-十字)")
    detect_on_image("pic/track_roundabout_perspective.png", "(透视-圆环)")

    # 检测逆透视恢复后的图像（应接近原始俯视图）
    detect_on_image("pic/track_cross_inver.png", "(逆透视恢复-十字)")
    detect_on_image("pic/track_roundabout_inver.png", "(逆透视恢复-圆环)")

    print("\n🎉 全部流程完成！")