import os
import torch
import torch.nn as nn
from torchvision import transforms
from torchvision.models import convnext_tiny
from PIL import Image
from io import BytesIO
import gdown  

class ImageService:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_classes = 124

        self.model_dir = os.path.join(os.getcwd(), "weights")
        self.model_path = os.path.join(self.model_dir, "convnext_tiny_best.pth")
        self.class_names_path = os.path.join(os.getcwd(), "classes.txt")
        self.model_url = os.getenv("MODEL_URL")
        # ====== Create storge save model ======
        os.makedirs(self.model_dir, exist_ok=True)

        if not os.path.exists(self.model_path):
            print("Đang tải model từ Google Drive...")
            gdown.download(self.model_url, self.model_path, quiet=False)
            print("Tải model thành công!")

        # ====== Load class names ======
        if not os.path.exists(self.class_names_path):
            raise FileNotFoundError("Không tìm thấy file classes.txt!")

        with open(self.class_names_path, "r") as f:
            self.class_names = [line.strip() for line in f]

        # ====== Load model ConvNeXt Tiny ======
        print("Đang khởi tạo mô hình ConvNeXt Tiny...")
        self.model = convnext_tiny(weights=None)
        self.model.classifier[2] = nn.Linear(
            self.model.classifier[2].in_features, self.num_classes
        )

        # Load weights
        state_dict = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)

        self.model = self.model.to(self.device)
        self.model.eval()
        print("Model đã sẵn sàng để sử dụng!")

        # ======Transform======
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    async def detect_image(self, file_bytes: bytes):
        """Nhận bytes ảnh, dự đoán class, trả về kết quả"""
        try:
            img = Image.open(BytesIO(file_bytes)).convert("RGB")
            img_tensor = self.transform(img).unsqueeze(0).to(self.device)

            with torch.no_grad():
                outputs = self.model(img_tensor)
                probs = torch.softmax(outputs, dim=1)
                pred_idx = torch.argmax(probs, dim=1).item()

            pred_class = self.class_names[pred_idx]
            pred_prob = round(probs[0][pred_idx].item(), 4)

            return {
                "predicted_class": pred_class,
                "probability": pred_prob
            }

        except Exception as e:
            raise RuntimeError(f"Lỗi khi dự đoán ảnh: {str(e)}")
