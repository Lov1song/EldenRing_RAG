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
        你是一名《艾尔登法环》资深玩家，根据以下检索到的资料回答用户问题。

        【检索到的资料】
        {context}

        【用户问题】
        {question}

        【回答要求】
        - 只根据资料回答，不要凭空捏造
        - 尽量简洁准确
        - 用中文回答
        """
        print("===== prompt =====")
        print(prompt)
        print("==================")
        answer = self.llm.generate(prompt)
        return answer