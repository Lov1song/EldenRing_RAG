# config.py（补充你的配置）
import os

# -------------------------- 你的本地模型配置 --------------------------
LOCAL_MODEL_PATH = "./models/all-MiniLM-L6-v2"  # 和你代码中的 model_path 一致
EMBEDDING_BATCH_SIZE = 32  # 和你代码中的 batch_size 一致

# -------------------------- 数据路径配置 --------------------------
MERGED_TEXT_PATH = "./data/final_data/final_merged_all.txt"  # 你的合并文本
PROCESSED_DATA_DIR = "./data/data_processed"  # 处理后输出目录
CHUNK_PATH = os.path.join(PROCESSED_DATA_DIR, "eldenring_chunks.json")  # 分块后文本路径
EMBEDDING_OUTPUT_PATH = os.path.join(PROCESSED_DATA_DIR, "eldenring_embeddings.npy")  # 你的embedding输出路径

# -------------------------- 其他复用配置 --------------------------
CLEAN_SKIP_PATTERNS = [
    r"领券购买.*?享优惠",
    r"加入.*?交流群.*?群号",
    r"更多相关内容请关注.*?专区",
    r"Map link", r"Map Link", r"\[.*?\]", r"More Info",
    r"See also", r"negation numbers", r"resistance numbers",
]
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
TOP_K = 3
SIMILARITY_THRESHOLD = 0.5