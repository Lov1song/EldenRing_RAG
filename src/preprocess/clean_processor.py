# clean_processor.py（修改版）
import json
import re
from base_processor import BaseProcessor

class CleanProcessor(BaseProcessor):
    def process(self, input_path: str, output_path: str, config: dict = None) -> None:
        # 默认配置（移除游戏相关术语和可能误判的符号）
        default_config = {
            "skip_patterns": [
                r"领券购买.*?享优惠",
                r"加入.*?交流群.*?群号",
                r"扫描以下二维码",
                # 移除可能误判的游戏术语和符号：r"%", r"\/", r"\d+,\d+", r"Talisman", r"Medallion"
            ],
            "min_length": 10,  # 降低默认最小长度
            "case_insensitive": True
        }
        config = {**default_config, **(config or {})}
        
        # 读取输入文件
        if input_path.endswith(".txt"):
            with open(input_path, "r", encoding="utf-8") as f:
                raw_text = f.read().strip()
            raw_texts = [t.strip() for t in raw_text.split("\n\n") if t.strip()]
        elif input_path.endswith(".json"):
            with open(input_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            raw_texts = data.get("text", [])
        else:
            raise ValueError(f"不支持的文件格式：{input_path}，仅支持 .txt 和 .json")
        
        # 核心清洗逻辑（添加调试日志）
        cleaned_texts = []
        flags = re.IGNORECASE if config["case_insensitive"] else 0
        for text in raw_texts:
            text = text.strip()
            # 过滤空文本（添加调试）
            if not text:
                print(f"[调试] 过滤空文本")
                continue
            # 过滤重复文本（添加调试）
            if text in cleaned_texts:
                print(f"[调试] 过滤重复文本：{text[:30]}...")
                continue
            # 过滤包含指定模式的文本（添加调试）
            matched = False
            for pattern in config["skip_patterns"]:
                if re.search(pattern, text, flags=flags):
                    print(f"[调试] 因匹配模式 [{pattern}] 过滤文本：{text[:30]}...")
                    matched = True
                    break
            if matched:
                continue
            # 过滤过短文本（添加调试）
            if len(text) < config["min_length"]:
                print(f"[调试] 因长度不足（{len(text)} < {config['min_length']}）过滤文本：{text[:30]}...")
                continue
            # 清洗特殊字符
            text = re.sub(r'\s+', ' ', text)
            cleaned_texts.append(text)
        
        # 保存结果
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"text": cleaned_texts}, f, ensure_ascii=False, indent=4)
        
        print(f"✔ 清洗完成！输入 {len(raw_texts)} 条，输出 {len(cleaned_texts)} 条，保存到：{output_path}")