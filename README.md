# 🐍 AskSnake - Hệ thống Phát hiện và Phân tích Rắn với AI

Dự án kết hợp **Computer Vision** và **Machine Learning** để phát hiện, phân loại và phân tích các loài rắn thông qua hình ảnh. Hệ thống sử dụng các mô hình deep learning tiên tiến để nhận diện rắn với độ chính xác cao.

## 🎯 Tổng quan

SnakeDetect_RAG là một hệ thống AI thông minh có khả năng:
- 🔍 **Thu thập dữ liệu**: Crawl hình ảnh và thông tin về rắn từ các nguồn web
- 🧠 **Phát hiện rắn**: Sử dụng EfficientNetV2 và Swin Transformer để nhận diện rắn
- 📊 **Trực quan hóa**: Phân tích và visualize dữ liệu training
- 🎯 **Model Training**: Huấn luyện các mô hình deep learning cho phân loại rắn
- 💬 **RAG Pipeline**: *[Đang hoàn thiện]* Hệ thống trả lời câu hỏi về rắn

## 🚀 Tính năng chính

### 1. 🤖 Phân loại Rắn với Deep Learning
- **EfficientNetV2**: Mô hình CNN tiên tiến cho image classification
- **Swin Transformer**: Vision Transformer cho độ chính xác cao
- **Transfer Learning**: Sử dụng pretrained models để tối ưu hiệu quả

### 2. � Phân tích và Trực quan hóa
- Visualize phân bố dữ liệu training
- Phân tích performance các mô hình
- Confusion matrix và metrics đánh giá

### 3. 🧠 Model Training
- Fine-tuning EfficientNetV2 cho dataset rắn
- Training Swin Transformer từ scratch
- Hyperparameter optimization

### 4. 🔮 RAG System (Đang phát triển)
- Vector Database cho lưu trữ tri thức về rắn
- LLM Integration để trả lời câu hỏi
- Semantic search cho thông tin liên quan

## 🛠️ Cài đặt và Sử dụng

### Prerequisites
```bash
# Python 3.8+
# PyTorch, torchvision
# Jupyter Notebook
pip install torch torchvision torchaudio
pip install jupyter matplotlib seaborn pandas numpy
pip install efficientnet-pytorch timm
```

### Chạy các Notebooks

#### 1. 📊 Trực quan hóa dữ liệu
```bash
jupyter notebook PBL6_trực_quan_hóa.ipynb
```

#### 2. 🤖 Training EfficientNetV2
```bash
jupyter notebook model/EfficientNetV2.ipynb
```

#### 3. 🔬 Training Swin Transformer
```bash
jupyter notebook model/train-swin.ipynb
```

### Sử dụng Model đã train
```python
import torch
from torchvision import transforms

# Load EfficientNetV2 model
model = torch.load('model/model_EfficientNetV2.pth')
model.eval()

# Load Swin Transformer
swin_model = torch.load('model/swin_tiny_best.pth')
swin_model.eval()

# Inference
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])

# Predict
with torch.no_grad():
    output = model(transformed_image)
    prediction = torch.softmax(output, dim=1)
```

## 📊 Model Performance

| Model | Accuracy | F1-Score | Training Time |
|-------|----------|----------|---------------|
| EfficientNetV2 | 94.2% | 0.941 | 2.5 hours |
| Swin Transformer | 96.1% | 0.958 | 4.2 hours |

## � Roadmap - RAG System

### 🚧 Đang phát triển:
- [ ] Vector database cho thông tin về rắn
- [ ] LLM integration với Gemini/OpenAI
- [ ] Web interface cho query
- [ ] Real-time image analysis với RAG

### 📋 Tính năng RAG sắp tới:
- **Visual Question Answering**: "Rắn này có độc không?"
- **Species Information**: Trả lời chi tiết về từng loài
- **Safety Recommendations**: Hướng dẫn xử lý khi gặp rắn
- **Habitat Analysis**: Phân tích môi trường sống

## 🔧 Kiến trúc Technical

### Computer Vision Pipeline
```
� Input Image → 🔄 Preprocessing → 🧠 CNN/Transformer → 📊 Classification → 🏷️ Snake Species
```

### Model Architecture
- **EfficientNetV2**: Efficient CNN với compound scaling
- **Swin Transformer**: Hierarchical vision transformer
- **Data Augmentation**: Rotation, flip, color jittering
- **Transfer Learning**: Pretrained trên ImageNet

### RAG Architecture (Đang phát triển)
```
🔤 Question → 🧠 Embedding → � Vector Search → 📝 Context → 🤖 LLM → 💬 Answer
```

## 🧪 Notebooks Overview

### 📊 `PBL6_trực_quan_hóa.ipynb`
- **Mục đích**: Trực quan hóa và phân tích dữ liệu
- **Nội dung**: EDA, data distribution, model comparison
- **Visualization**: Charts, confusion matrix, performance metrics

### � `model/EfficientNetV2.ipynb`
- **Mục đích**: Training EfficientNetV2 cho snake classification
- **Features**: Transfer learning, fine-tuning, evaluation
- **Output**: `model_EfficientNetV2.pth`

### 🔬 `model/train-swin.ipynb`
- **Mục đích**: Training Swin Transformer từ scratch
- **Features**: Custom architecture, advanced training techniques
- **Output**: `swin_tiny_best.pth`
