import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from retrieval.retriever import Retriever
from llm.ollama_client import OllamaClient

class RAG_QA:
    def __init__(self,retriever:Retriever,llm:OllamaClient):
        self.retriever = retriever
        self.llm = llm
    def answer(self,question):
        hits = self.retriever.search(question)
        # print("检索 hits:", hits)
        context = "\n\n".join([f"[{i+1}] {text}" for i,(_,text,_) in enumerate(hits)])

        prompt = f"""
        你是《艾尔登法环》攻略专家，必须严格按照以下规则回答：
        1. 仅使用【检索到的资料】中的信息，绝对不能编造资料中没有的内容；
        2. 如果是“如何获得某物品”：提取具体步骤（包括地点、需要击败的敌人、关键操作），按执行顺序排列；
        3. 如果是“如何击败某BOSS”：提取战斗步骤（包括优先攻击目标、躲避技巧、辅助手段），突出核心要点；
        4. 如果是“***是谁”时，提取人物的重要属性，按照顺序排列；
        5. 资料中没有相关答案时，直接回复“抱歉，没有找到该问题的相关攻略”；
        6. 回答简洁明了，分点（或按逻辑顺序）说明，不要冗余。

        【检索到的资料】
        {context}

        【用户问题】
        {question}

        【回答】
        """
        print("===== prompt =====")
        print(prompt)
        print("==================")
        answer = self.llm.generate(prompt)
        return answer