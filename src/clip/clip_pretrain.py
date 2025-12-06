import os
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import clip
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split

# ===================== 配置 =====================
CSV_PATH = "./data/clip_pre/game_image_labels.csv"  # 标注数据路径
BATCH_SIZE = 8  # 批次大小（小一点适合显存小的设备）
EPOCHS = 50  # 训练轮次（10-20轮足够）
LEARNING_RATE = 1e-4  # 学习率（小一点避免破坏原模型）
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ===================== 数据集定义 =====================
class GameImageDataset(Dataset):
    def __init__(self, image_paths, labels, preprocess):
        self.image_paths = image_paths
        self.labels = labels  # 二进制标签（如[1,0,1]表示包含第0和第2个标签）
        self.preprocess = preprocess

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")
        image = self.preprocess(image).to(DEVICE)  # CLIP预处理
        label = torch.tensor(self.labels[idx], dtype=torch.float32).to(DEVICE)
        return image, label

# ===================== 微调模型定义 =====================
class ClipFineTuner(nn.Module):
    def __init__(self, clip_model, num_labels):
        super().__init__()
        self.clip = clip_model
        # 冻结CLIP大部分层（只训练最后一层）
        for param in self.clip.parameters():
            param.requires_grad = False  # 冻结
        # 新增一个分类头（适配游戏标签）
        self.classifier = nn.Linear(512, num_labels)  # 512是CLIP输出特征维度

    def forward(self, image):
        # 用CLIP提取图片特征
        with torch.no_grad():  # 冻结时不计算梯度
            image_features = self.clip.encode_image(image)
        # 特征归一化
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)
        # 分类头输出标签概率
        logits = self.classifier(image_features)
        return logits

# ===================== 训练流程 =====================
def main():
    # 1. 加载标注数据
    df = pd.read_csv(CSV_PATH)
    image_paths = df["image_path"].tolist()
    labels = df["label"].apply(lambda x: x.split()).tolist()  # 标签拆分（如["玛莲妮亚", "BOSS截图"]）

    # 2. 标签编码（转为二进制向量）
    mlb = MultiLabelBinarizer()
    labels_bin = mlb.fit_transform(labels)  # 如["玛莲妮亚", "BOSS"] → [1,0,1,...]
    num_labels = len(mlb.classes_)  # 标签总数
    print(f"✅ 标签列表：{mlb.classes_}，共{num_labels}个标签")

    # 3. 划分训练集和验证集（8:2）
    train_paths, val_paths, train_labels, val_labels = train_test_split(
        image_paths, labels_bin, test_size=0.2, random_state=42
    )

    # 4. 加载CLIP基础模型和预处理工具
    clip_model, preprocess = clip.load("ViT-B/32", device=DEVICE)

    # 5. 创建数据集和数据加载器
    train_dataset = GameImageDataset(train_paths, train_labels, preprocess)
    val_dataset = GameImageDataset(val_paths, val_labels, preprocess)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    # 6. 初始化微调模型、损失函数、优化器
    model = ClipFineTuner(clip_model, num_labels).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss()  # 多标签分类损失
    optimizer = optim.Adam(model.classifier.parameters(), lr=LEARNING_RATE)  # 只优化分类头

    # 7. 开始训练
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0.0
        for images, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(images)  # 模型预测
            loss = criterion(outputs, labels)  # 计算损失
            loss.backward()  # 反向传播
            optimizer.step()  # 更新参数
            train_loss += loss.item() * images.size(0)

        # 验证（可选）
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for images, labels in val_loader:
                outputs = model(images)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * images.size(0)

        print(f"Epoch {epoch+1}/{EPOCHS}")
        print(f"训练损失：{train_loss/len(train_dataset):.4f}")
        print(f"验证损失：{val_loss/len(val_dataset):.4f}\n")

    # 8. 保存微调后的模型（只保存分类头，CLIP主体无需重复保存）
    torch.save(model.classifier.state_dict(), "./data/clip_pre/clip_game_classifier.pth")
    print(f"✅ 微调完成！分类头保存为：./data/clip_pre/clip_game_classifier.pth")
    print(f"标签映射表：{mlb.classes_}")  # 保存这个列表，后续预测需要

if __name__ == "__main__":
    main()