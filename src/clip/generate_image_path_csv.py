import os
import csv
import sys

IMG_ROOT_DIR = "./data/game_images"

def generate_image_csv(target_timestamp=None):
    """
    自动生成包含图片路径的CSV文件
    :param target_timestamp: 图片批次时间戳（如"20251203_151414"）
    """
    # 1. 检查图片根目录是否存在
    if not os.path.exists(IMG_ROOT_DIR):
        print(f"❌ 图片根目录不存在：{IMG_ROOT_DIR}")
        return
    
    # 2. 找到目标批次目录
    all_timestamps = [d for d in os.listdir(IMG_ROOT_DIR) 
                      if os.path.isdir(os.path.join(IMG_ROOT_DIR, d))]
    if not all_timestamps:
        print(f"❌ {IMG_ROOT_DIR} 下没有时间戳批次目录")
        return
    
    # 3. 确定要处理的图片批次（指定批次或最新批次）
    if target_timestamp and target_timestamp in all_timestamps:
        img_batch_dir = os.path.join(IMG_ROOT_DIR, target_timestamp)
    else:
        all_timestamps.sort(reverse=True)
        target_timestamp = all_timestamps[0]
        img_batch_dir = os.path.join(IMG_ROOT_DIR, target_timestamp)
    print(f"📌 处理图片批次：{target_timestamp}，目录：{img_batch_dir}")
    
    # 4. 获取目录下所有图片文件（支持jpg/png/jpeg）
    img_extensions = (".jpg", ".jpeg", ".png")
    img_files = [f for f in os.listdir(img_batch_dir) 
                 if f.lower().endswith(img_extensions)]
    
    if not img_files:
        print(f"⚠️ {img_batch_dir} 下没有图片文件（支持{img_extensions}）")
        return
    
    # 5. 生成CSV文件（保存到项目根目录）
    csv_path = "game_image_labels.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["image_path", "label"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # 写入表头
        writer.writeheader()
        
        # 写入图片路径（label先留空）
        for img_file in img_files:
            # 获取绝对路径（避免后续读取时路径错误）
            img_abs_path = os.path.abspath(os.path.join(img_batch_dir, img_file))
            writer.writerow({"image_path": img_abs_path, "label": ""})  # label留空
    
    print(f"🎉 CSV文件生成成功！路径：{os.path.abspath(csv_path)}")
    print(f"📊 共写入 {len(img_files)} 张图片的路径，label列已留空，请手动补充标签")

if __name__ == "__main__":
    generate_image_csv(target_timestamp="20251203_151414")