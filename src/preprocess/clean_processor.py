# clean_processor.py（关键修改）
import json
import re
from base_processor import BaseProcessor

class CleanProcessor(BaseProcessor):
    def process(self, input_path: str, output_path: str, config: dict = None) -> None:
        default_config = {
            "skip_patterns": [
                r"领券购买.*?享优惠",
                r"加入.*?交流群.*?群号",
                r"更多相关内容请关注.*?专区",
                r"Map link", r"Map Link", r"\[.*?\]", r"More Info",
                r"See also", r"negation numbers", r"resistance numbers",
            ],
            "min_length": 10,
            "case_insensitive": True
        }
        config = {**default_config, **(config or {})}
        # 读取输入文件（原有逻辑不变）
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
        
        # 核心清洗逻辑（新增：过滤攻略文本的冗余垃圾信息）
        cleaned_texts = []
        flags = re.IGNORECASE if config["case_insensitive"] else 0
        for text in raw_texts:
            text = text.strip()
            
            # 1. 过滤空文本和重复文本（原有逻辑）
            if not text:
                print(f"[调试] 过滤空文本")
                continue
            if text in cleaned_texts:
                print(f"[调试] 过滤重复文本：{text[:30]}...")
                continue
            
            # 2. 过滤skip_patterns中的模式（原有逻辑）
            matched = False
            for pattern in config["skip_patterns"]:
                if re.search(pattern, text, flags=flags):
                    print(f"[调试] 因匹配模式 [{pattern}] 过滤文本：{text[:30]}...")
                    matched = True
                    break
            if matched:
                continue
            
            # 3. 新增：删除攻略文本中的冗余垃圾信息（关键修改）
            # 匹配并删除 "更多相关内容请关注..." 到 "文章内容导航" 之间的所有内容
            text = re.sub(r"更多相关内容请关注.*?文章内容导航.*?\d+页.*?", "", text, flags=re.DOTALL)
            # 删除 "责任编辑.*?" 相关内容
            text = re.sub(r"责任编辑.*?", "", text)
            # 删除 "友情提示.*?翻页" 相关内容
            text = re.sub(r"友情提示.*?翻页", "", text)
            # 删除多余的空格和换行
            text = re.sub(r"\s+", " ", text).strip()
            
            # 4. 过滤过短文本（原有逻辑）
            if len(text) < config["min_length"]:
                print(f"[调试] 因长度不足（{len(text)} < {config['min_length']}）过滤文本：{text[:30]}...")
                continue
            
            cleaned_texts.append(text)

        # 保存结果（原有逻辑）
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"text": cleaned_texts}, f, ensure_ascii=False, indent=4)
        
        print(f"✔ 清洗完成！输入 {len(raw_texts)} 条，输出 {len(cleaned_texts)} 条，保存到：{output_path}")