"""
透视变换脚本（正向映射版）
用户指定原图四个角在输出图像中的目标位置，程序自动计算并应用透视变换。
"""

from PIL import Image
import numpy as np

def apply_perspective_transform(
    input_path,
    output_path,
    dst_corners=None,
    src_corners=None,
    output_size=None
):
    """
    根据用户指定的原图角点目标位置进行透视变换。

    参数:
        input_path: 输入图片路径
        output_path: 输出图片路径
        dst_corners: 原图四个角点在输出图像中的目标位置。
                     顺序必须为: 左上, 右上, 右下, 左下。
        src_corners: 原图四个角点在输入图像中的位置
                     顺序必须为: 左上, 右上, 右下, 左下。
        output_size: 输出图像尺寸 (width, height)，默认为原图大小。
    """
    img = Image.open(input_path)
    orig_w, orig_h = img.size

    if output_size is None:
        dst_w, dst_h = orig_w, orig_h
    else:
        dst_w, dst_h = output_size

    # 计算透视变换矩阵（从输出图像到原图像的逆映射）
    matrix = _find_perspective_matrix(dst_corners, src_corners)

    # 应用变换
    coeffs = matrix.flatten()[:8]
    transformed = img.transform(
        (dst_w, dst_h),
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC
    )

    transformed.save(output_path)
    print(f"✅ 透视变换完成: {input_path} -> {output_path}")
    print(f"   目标角点: {dst_corners}")


def _find_perspective_matrix(src_points, dst_points):
    """
    计算透视变换矩阵 H，使得 src_points 映射到 dst_points。
    返回 3x3 矩阵。
    """
    A = []
    for (x, y), (u, v) in zip(src_points, dst_points):
        A.append([x, y, 1, 0, 0, 0, -u*x, -u*y])
        A.append([0, 0, 0, x, y, 1, -v*x, -v*y])
    A = np.array(A, dtype=np.float64)
    B = np.array(dst_points, dtype=np.float64).reshape(-1)
    h = np.linalg.lstsq(A, B, rcond=None)[0]
    H = np.append(h, 1).reshape(3, 3)
    return H


def batch_transform_all(w, h, change):
    """批量处理 generate.py 生成的三张图片"""
    images = ["pic/track_normal.png", "pic/track_cross.png", "pic/track_roundabout.png"]

    # 您可以在这里自由修改目标角点，获得不同的透视效果
    # 示例：您描述的效果 —— 顶部向内收缩 100 像素
    dst_corners = [
        (0, 0),      # 原图左上角移到 (100,0)
        (w, 0),      # 原图右上角移到 (540,0)
        (w, h),    # 右下角保持
        (0, h)       # 左下角保持
    ]

    src_corners = [
        (0, 0),  # 左上
        (w, 0),  # 右上
        (w * (1 - change), h),  # 右下
        (w * change, h)  # 左下
    ]

    for name in images:
        out_name = name.replace(".png", "_perspective.png")
        apply_perspective_transform(
            name,
            out_name,
            dst_corners=dst_corners,
            src_corners=src_corners,
            output_size=(w, h)   # 可调整输出尺寸
        )

    print("   - track_normal.png / track_normal_perspective.png")
    print("   - track_cross.png / track_cross_perspective.png")
    print("   - track_roundabout.png / track_roundabout_perspective.png")


if __name__ == "__main__":
    pass