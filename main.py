"""
智能车赛道测试数据生成与透视变换集成脚本。
依次执行：
1. 生成平视二值图 (generate.py)
2. 施加倾斜透视变换 (apply_perspective.py)
"""

import subprocess
import sys

from generate import generate_all_test_images
from apply_perspective import batch_transform_all
from Inverse_transformation import estimate_ipm_matrix_from_lanes

def run_script(script_name):
    """运行指定的 Python 脚本"""
    print(f"\n>>> 正在运行: {script_name}")
    result = subprocess.run([sys.executable, script_name], capture_output=False)
    if result.returncode != 0:
        print(f"❌ 脚本 {script_name} 执行失败，退出码: {result.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    # 第一步：生成原始平视图
    w, h = 1280, 960
    track_width = 100
    r_c_y = h / 2
    ring_radius = 100
    change = 0.3
    generate_all_test_images(w, h, track_width, r_c_y, ring_radius)

    # 第二步：应用透视变换
    batch_transform_all(w, h, change)


    # 第三步：反解透视变换
    estimate_ipm_matrix_from_lanes(in_path ="pic/track_roundabout_perspective.png", out_path="pic/track_roundabout_inver.png")

