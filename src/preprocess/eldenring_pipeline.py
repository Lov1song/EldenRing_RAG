# eldenring_pipeline.py（修改版）
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from clean_processor import CleanProcessor
from chunk_processor import ChunkProcessor
from embedding_processor import EmbeddingProcessor
from faiss_processor import FaissProcessor
import config

def run_eldenring_pipeline():
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    
    pipeline_config = [
        {
            "processor": CleanProcessor,
            "input": config.MERGED_TEXT_PATH,
            "output": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_cleaned.json"),
            "config": {
                "skip_patterns": config.CLEAN_SKIP_PATTERNS,
                "min_length": 10,  
                "case_insensitive": True
            }
        },
        {
            "processor": ChunkProcessor,
            "input": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_cleaned.json"),
            "output": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_chunks.json"),
            "config": {
                "chunk_size": config.CHUNK_SIZE,
                "overlap": config.CHUNK_OVERLAP,
                "split_pattern": r'(?<=[。？！])\s+'
            }
        },
        {
            "processor": EmbeddingProcessor,
            "input": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_chunks.json"),
            "output": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_embeddings.npy"),
            "config": {
                "model_path": config.LOCAL_MODEL_PATH,
                "batch_size": config.EMBEDDING_BATCH_SIZE
            }
        },
        {
            "processor": FaissProcessor,
            "input": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_embeddings.npy"),
            "output": os.path.join(config.PROCESSED_DATA_DIR, "eldenring_index.faiss")
        }
    ]

    for step in pipeline_config:
        print(f"\n===== 执行步骤：{step['processor'].__name__} =====")
        try:
            processor = step["processor"]()
            processor.process(
                input_path=step["input"],
                output_path=step["output"],
                config=step.get("config", {})
            )
        except Exception as e:
            print(f"❌ 步骤执行失败：{str(e)}")
            break

if __name__ == "__main__":
    run_eldenring_pipeline()