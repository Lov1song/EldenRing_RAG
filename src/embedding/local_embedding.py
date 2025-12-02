import torch
from transformers import AutoTokenizer, AutoModel

class LocalEmbedding:
    def __init__(self,model_path=""):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
        self.model.eval()
    def encode(self,texts,batch_size=32):
        all_embeddings = []
        for i in range(0,len(texts),batch_size):
            batch = texts[i:i+batch_size]
            encoded_input = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                return_tensors='pt'
            ).to(self.device)
            
            with torch.no_grad():
                output = self.model(**encoded_input)
            
            embeddings = output.last_hidden_state.mean(dim=1)
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
            all_embeddings.append(embeddings.cpu())

        return torch.cat(all_embeddings)