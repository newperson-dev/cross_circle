import numpy as np
from PIL import Image, ImageDraw

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

def extrapolate_line(x1, y1, x2, y2, y_target):
    """已知两点 (x1,y1) 和 (x2,y2)，求 y=y_target 时的 x 坐标（线性外推）"""
    if y1 == y2:
        return x1
    return x1 + (x2 - x1) * (y_target - y1) / (y2 - y1)

def inverse_transform_image(input_path, output_path, output_size=None):
    # 读取图像并二值化
    img = Image.open(input_path).convert('L')
    binary_img = np.array(img) > 128
    h, w = binary_img.shape

    if output_size is None:
        dst_w, dst_h = w, h
    else:
        dst_w, dst_h = output_size

    def get_edge_points(row):
        white = np.where(binary_img[row])[0]
        if len(white) >= 2:
            return white[0], white[-1]
        return None, None

    y_bottom = h - 10
    y_top = 10
    left_bottom, right_bottom = get_edge_points(y_bottom)
    left_top, right_top = get_edge_points(y_top)

    if None in (left_bottom, right_bottom, left_top, right_top):
        raise ValueError("无法检测到完整赛道边线")

    print("检测到的边线点：")
    print(f"  左上: ({left_top}, {y_top})")
    print(f"  右上: ({right_top}, {y_top})")
    print(f"  左下: ({left_bottom}, {y_bottom})")
    print(f"  右下: ({right_bottom}, {y_bottom})")

    # ---------- 线性外推边界点 ----------
    y_top_target = 0
    y_bottom_target = h
    left_top_extrap = extrapolate_line(left_top, y_top, left_bottom, y_bottom, y_top_target)
    left_bottom_extrap = extrapolate_line(left_top, y_top, left_bottom, y_bottom, y_bottom_target)
    right_top_extrap = extrapolate_line(right_top, y_top, right_bottom, y_bottom, y_top_target)
    right_bottom_extrap = extrapolate_line(right_top, y_top, right_bottom, y_bottom, y_bottom_target)

    print("📍 外推边界点（y=0 和 y={}）：".format(h))
    print(f"   左上: ({left_top_extrap:.2f}, 0)")
    print(f"   右上: ({right_top_extrap:.2f}, 0)")
    print(f"   右下: ({right_bottom_extrap:.2f}, {h})")
    print(f"   左下: ({left_bottom_extrap:.2f}, {h})")

    change = (1-(right_top_extrap-left_top_extrap)/(right_bottom_extrap-left_bottom_extrap))/2
    """
    print(f'    change: {change:.2f}')
    """
    # ------------------------------------

    # 绘制调试图像：标记检测点（红色）和外推点（绿色）
    debug_img = img.convert('RGB')
    draw = ImageDraw.Draw(debug_img)
    # 检测点：红色圆点
    detect_pts = [(left_top, y_top), (right_top, y_top), (right_bottom, y_bottom), (left_bottom, y_bottom)]
    for pt in detect_pts:
        draw.ellipse([pt[0]-6, pt[1]-6, pt[0]+6, pt[1]+6], fill='red', outline='white', width=2)
    # 外推点：绿色圆点
    extrap_pts = [
        (left_top_extrap, 0),
        (right_top_extrap, 0),
        (right_bottom_extrap, h),
        (left_bottom_extrap, h)
    ]
    for pt in extrap_pts:
        draw.ellipse([pt[0]-8, pt[1]-8, pt[0]+8, pt[1]+8], fill='green', outline='white', width=2)
    # 可选：连接左侧外推点与右侧外推点，显示延伸线
    draw.line([extrap_pts[0], extrap_pts[3]], fill='blue', width=2)  # 左侧边线延伸
    draw.line([extrap_pts[1], extrap_pts[2]], fill='blue', width=2)  # 右侧边线延伸
    debug_img.save('debug_points_with_extrap.png')
    print("已保存带检测点(红)和外推点(绿)的调试图像: debug_points_with_extrap.png")

    # 源点：透视图像中检测到的四边形（顺时针：左上、右上、右下、左下）
    dst_pts = [
        (0, 0),  # 左上
        (w, 0),  # 右上
        (w * (1 - change), h),  # 右下
        (w * change, h)  # 左下
    ]
    # 目标点：期望的俯视图矩形（对应原图的四个角）
    target_left_x = 0
    target_right_x = dst_w
    src_pts = [
        (0, 0),
        (w, 0),
        (w, h),
        (0, h)
    ]

    # 计算从目标图像（俯视图）到源图像（透视图像）的映射矩阵 H
    H = _find_perspective_matrix(dst_pts, src_pts)
    coeffs = H.flatten()[:8]

    # 应用变换
    recovered = img.transform(
        (dst_w, dst_h),
        Image.PERSPECTIVE,
        coeffs,
        Image.BICUBIC
    )
    recovered.save(output_path)
    print(f"✅ 逆透视变换完成: {input_path} -> {output_path}")

if __name__ == "__main__":
    inverse_transform_image("pic/track_roundabout_perspective.png", "pic/track_roundabout_inver.png", output_size=(1280, 960))