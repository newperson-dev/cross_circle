import numpy as np
from PIL import Image

class TrackElementDetector:
    def __init__(self, image_path):
        """加载图像并转换为二值化 numpy 数组"""
        img = Image.open(image_path).convert('L')          # 灰度图
        # 若输入非二值，可在此处加阈值处理，此处假设已是黑白二值
        self.binary = np.array(img) > 128                  # True = 白色赛道，False = 黑色背景
        self.h, self.w = self.binary.shape

    def _get_left_right_edges(self, row):
        """返回指定行左右边界列索引（无边界时返回 -1）"""
        white_idx = np.where(self.binary[row])[0]
        if len(white_idx) < 2:
            return -1, -1
        return white_idx[0], white_idx[-1]

    def _find_corners(self, edges):
        """检测边线序列中的拐点（斜率突变点）"""
        corners = []
        # 滑动窗口计算斜率变化
        for i in range(1, len(edges)-1):
            if edges[i][0] != -1 and edges[i-1][0] != -1 and edges[i+1][0] != -1:
                dx1 = edges[i][0] - edges[i-1][0]
                dx2 = edges[i+1][0] - edges[i][0]
                if abs(dx1 - dx2) > 8:          # 斜率突变阈值
                    corners.append(i)
        return corners

    def detect_cross(self):
        """检测十字路口"""
        edges = [self._get_left_right_edges(r) for r in range(self.h)]
        left_edges = [e[0] for e in edges]
        right_edges = [e[1] for e in edges]

        # 找到左右边线拐点行索引
        left_corners = self._find_corners([(l, 0) for l in left_edges])
        right_corners = self._find_corners([(r, 0) for r in right_edges])

        # 十字判定：拐点数量 ≥ 3 且拐点分布范围较大
        total_corners = len(left_corners) + len(right_corners)
        if total_corners >= 3:
            # 额外检查中间区域白色占比
            mid_row = self.h // 2
            white_ratio = np.sum(self.binary[mid_row-10:mid_row+10, :]) / (20 * self.w)
            if white_ratio > 0.4:               # 中间大面积白色
                return True
        return False

    def detect_roundabout(self):
        """检测圆环（前方大面积黑色障碍物）"""
        # 取图像下半部分（近处）作为分析区
        roi = self.binary[self.h*2//3:, :]
        h_roi, w_roi = roi.shape

        # 寻找中心区域最大黑色连通宽度
        center_col = w_roi // 2
        max_black_width = 0
        for r in range(h_roi-10, -1, -1):       # 从下往上扫描
            left, right = center_col, center_col
            while left > 0 and not roi[r, left]:
                left -= 1
            while right < w_roi-1 and not roi[r, right]:
                right += 1
            width = right - left
            if width > max_black_width:
                max_black_width = width

        # 圆环判定：中心黑块宽度 > 图像宽度的 30%
        if max_black_width > 0.3 * w_roi:
            # 同时两侧必须有白色赛道
            left_region = roi[:, :w_roi//4]
            right_region = roi[:, 3*w_roi//4:]
            if np.any(left_region) and np.any(right_region):
                return True
        return False

    def run(self):
        """执行检测并输出结果"""
        print("检测结果：")
        print(f"十字路口: {'存在' if self.detect_cross() else '不存在'}")
        print(f"圆环赛道: {'存在' if self.detect_roundabout() else '不存在'}")

# ------------------- 使用示例 -------------------
if __name__ == "__main__":
    # 替换为你的二值化赛道图片路径
    detector = TrackElementDetector("track_binary.png")
    detector.run()