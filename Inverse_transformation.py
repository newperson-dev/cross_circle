import numpy as np
from PIL import Image
from apply_perspective import apply_perspective_transform

def estimate_ipm_matrix_from_lanes(in_path, out_path):
    """
    从二值化透视图像中估计逆透视变换矩阵。
    假设：赛道左右边线在世界坐标系中平行且等宽。
    返回：3x3 逆透视矩阵（可将透视图像映射到俯视图）。
    :param in_path: 输入图片路径.
           out_path: 输出图片路径
    """
    img = Image.open(in_path).convert('L')  # 转为灰度图
    binary_img = np.array(img) > 128
    h, w = binary_img.shape

    # 1. 扫描底部和顶部的左右边线点
    def get_edge_points(row):
        white = np.where(binary_img[row])[0]
        if len(white) >= 2:
            return white[0], white[-1]  # 左、右边界
        return None, None

    # 取底部附近行（如 row = h-20）
    left_bottom, right_bottom = get_edge_points(h - 20)
    # 取顶部附近行（如 row = 50）
    left_top, right_top = get_edge_points(50)

    if None in (left_bottom, right_bottom, left_top, right_top):
        raise ValueError("无法检测到完整赛道边线")

    # 2. 设定目标俯视图中的对应点（假设输出宽度为 w，高度为 h）
    #    我们希望在俯视图中赛道左右边线是垂直的，且宽度固定。
    #    这里简单设定：左边界在 x = w/4，右边界在 x = 3w/4
    target_left_x = w // 4
    target_right_x = 3 * w // 4

    # 源点（透视图像中的四个点）
    src_pts = np.float32([
        [left_bottom, h - 20],  # 左下
        [right_bottom, h - 20],  # 右下
        [right_top, 50],  # 右上
        [left_top, 50]  # 左上
    ])

    # 目标点（俯视图中的矩形）
    dst_pts = np.float32([
        [target_left_x, h],  # 左下
        [target_right_x, h],  # 右下
        [target_right_x, 0],  # 右上
        [target_left_x, 0]  # 左上
    ])

    # 3. 计算透视变换矩阵（从透视图像到俯视图）
    #    使用最小二乘法求解单应矩阵
    matrix = apply_perspective_transform(input_path=in_path, output_path=out_path, dst_corners=dst_pts, src_corners=src_pts)