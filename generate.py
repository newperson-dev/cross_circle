from PIL import Image, ImageDraw

def create_base_canvas(width=640, height=480, bg_color=0):
    return Image.new('L', (width, height), bg_color)

def draw_straight_track(draw, width, height, track_width=100, center_x=None):
    if center_x is None:
        center_x = width // 2
    half = track_width // 2
    draw.rectangle([center_x - half, 0, center_x + half, height], fill=255)

def draw_cross_track(draw, width, height, track_width=100):
    cx = width // 2
    half = track_width // 2
    # 纵向主道
    draw.rectangle([cx - half, 0, cx + half, height], fill=255)
    # 横向横道
    cross_y1 = height // 3
    cross_y2 = 2 * height // 3
    draw.rectangle([0, cross_y1, width, cross_y2], fill=255)

def draw_roundabout_track(draw, width, height, track_width=100, ring_radius=130, r_c_y = 100):
    cx = width // 2
    half = track_width // 2

    # 底部直道
    straight_top = height // 2 + 20
    draw.rectangle([cx - half, straight_top, cx + half, height], fill=255)

    # 内圆半径与圆环中心
    inner_r = ring_radius - track_width
    ring_center_x = cx + half + inner_r
    ring_center_y = r_c_y

    outer_r = ring_radius

    # 白色圆环
    draw.ellipse([ring_center_x - outer_r, ring_center_y - outer_r,
                  ring_center_x + outer_r, ring_center_y + outer_r], fill=255)
    draw.ellipse([ring_center_x - inner_r, ring_center_y - inner_r,
                  ring_center_x + inner_r, ring_center_y + inner_r], fill=0)

    # 上半部分直道（环岛分叉前的主道）
    draw.rectangle([cx - half, 0, cx + half, straight_top], fill=255)

def generate_all_test_images(w,h,track_width=100,r_c_y=100,ring_radius=130):


    # 直道
    img1 = create_base_canvas(w, h)
    draw1 = ImageDraw.Draw(img1)
    draw_straight_track(draw1, w, h, track_width)
    img1.save("pic/track_normal.png")
    print("✅ track_normal.png")

    # 十字
    img2 = create_base_canvas(w, h)
    draw2 = ImageDraw.Draw(img2)
    draw_cross_track(draw2, w, h, track_width)
    img2.save("pic/track_cross.png")
    print("✅ track_cross.png")

    # 圆环（正确版本）
    img3 = create_base_canvas(w, h)
    draw3 = ImageDraw.Draw(img3)
    draw_roundabout_track(draw3, w, h, track_width, ring_radius=200, r_c_y=r_c_y)
    img3.save("pic/track_roundabout.png")
    print("✅ track_roundabout.png (内圆与直道右侧相切)")

if __name__ == "__main__":
    generate_all_test_images()
    print("全部测试图片生成完毕！")