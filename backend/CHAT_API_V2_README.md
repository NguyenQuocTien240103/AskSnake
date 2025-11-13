# Chat API v2 - RAG với Memory và Auto-Summary

## 🎯 Tổng quan

Chat API mới với đầy đủ tính năng:
- ✅ Lưu chat history vào MongoDB
- ✅ LangChain memory (10 messages gần nhất)
- ✅ RAG với Qdrant vector store
- ✅ Tự động tóm tắt khi hội thoại dài
- ✅ Hỗ trợ upload ảnh rắn + hỏi đáp

## 📋 Luồng hoạt động

```
User gửi message
    ↓
(1) Lưu vào MongoDB (role=human)
    ↓
(2) Lấy 10 messages gần nhất + summary
    ↓
(3) RAG: Query Qdrant để lấy context
    ↓
(4) LLM: Ghép prompt + context + history
    ↓
(5) Lưu response vào MongoDB (role=ai)
    ↓
(6) Auto-summary nếu >20 messages
```

## 🔌 API Endpoints

### 1. Gửi Message (Main Chat)

**POST** `/api/chat/message`

**Form Data:**
- `user_id` (string, required): ID của user
- `message` (string, required): Tin nhắn từ user
- `chat_id` (string, optional): ID của chat (null để tạo mới)
- `file` (file, optional): Ảnh rắn để detect

**Response:**
```json
{
  "chat_id": "507f1f77bcf86cd799439011",
  "message": "Rắn hổ mang (Naja naja) là loài rắn độc thuộc họ Elapidae...",
  "context_used": 5,
  "was_summarized": false
}
```

**Ví dụ cURL:**
```bash
# Tạo chat mới (không có chat_id)
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=user123" \
  -F "message=Rắn hổ mang có độc không?"

# Tiếp tục chat hiện tại
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=user123" \
  -F "chat_id=507f1f77bcf86cd799439011" \
  -F "message=Chúng sống ở đâu?"

# Upload ảnh + hỏi
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=user123" \
  -F "chat_id=507f1f77bcf86cd799439011" \
  -F "message=Con này có nguy hiểm không?" \
  -F "file=@snake_image.jpg"
```

### 2. Lấy lịch sử chat

**GET** `/api/chat/history/{chat_id}?limit=50`

**Response:**
```json
{
  "chat_id": "507f1f77bcf86cd799439011",
  "title": "Chat về rắn hổ mang",
  "summary": "Conversation about cobra snake characteristics...",
  "messages": [
    {
      "role": "human",
      "content": "Rắn hổ mang có độc không?",
      "timestamp": "2024-01-01T10:00:00",
      "metadata": {}
    },
    {
      "role": "ai",
      "content": "Có, rắn hổ mang là loài rắn độc...",
      "timestamp": "2024-01-01T10:00:05",
      "metadata": {
        "context_chunks_used": 5,
        "reranking_used": true
      }
    }
  ],
  "total_messages": 12,
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T11:30:00"
}
```

### 3. Liệt kê các chats của user

**GET** `/api/chat/list/{user_id}?limit=50`

**Response:**
```json
{
  "user_id": "user123",
  "total_chats": 3,
  "chats": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "title": "Chat về rắn hổ mang",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T11:30:00",
      "message_count": 12
    }
  ]
}
```

### 4. Xóa chat

**DELETE** `/api/chat/{chat_id}`

**Response:**
```json
{
  "message": "Chat deleted successfully",
  "chat_id": "507f1f77bcf86cd799439011"
}
```

### 5. Tạo lại summary

**POST** `/api/chat/regenerate-summary/{chat_id}`

**Response:**
```json
{
  "message": "Summary regenerated successfully",
  "chat_id": "507f1f77bcf86cd799439011",
  "summary": "This conversation covered information about cobras..."
}
```

## 🗄️ MongoDB Schema

### Collection: `chats`

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "user_id": "user123",
  "title": "Chat về rắn hổ mang",
  "messages": [
    {
      "role": "human",  // "human", "ai", or "system"
      "content": "Rắn hổ mang có độc không?",
      "timestamp": ISODate("2024-01-01T10:00:00Z"),
      "metadata": {
        "snake_detected": "Naja naja",
        "probability": 0.95
      }
    }
  ],
  "summary": "Conversation about cobra characteristics and habitat...",
  "created_at": ISODate("2024-01-01T10:00:00Z"),
  "updated_at": ISODate("2024-01-01T11:30:00Z"),
  "is_active": true
}
```

## ⚙️ Cấu hình

Trong file `chat_router_v2.py`:

```python
MAX_MESSAGES_BEFORE_SUMMARY = 20  # Tự động tóm tắt sau 20 messages
RECENT_MESSAGES_COUNT = 10        # Lấy 10 messages gần nhất để làm context
```

## 🔧 Cài đặt

1. Đảm bảo MongoDB đang chạy và có kết nối trong `.env`:
```env
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=asksnake
```

2. Các dependencies cần thiết (đã có trong requirements.txt):
- `motor` - MongoDB async driver
- `pymongo` - MongoDB driver
- `pydantic` - Data validation
- `langchain` - Memory management

3. Khởi động server:
```bash
cd backend
fastapi dev main.py
```

## 📝 Ví dụ sử dụng Python

```python
import requests

# Tạo chat mới
response = requests.post(
    "http://localhost:8000/api/chat/message",
    data={
        "user_id": "user123",
        "message": "Rắn hổ mang có độc không?"
    }
)
result = response.json()
chat_id = result["chat_id"]
print(f"AI: {result['message']}")

# Tiếp tục hỏi
response = requests.post(
    "http://localhost:8000/api/chat/message",
    data={
        "user_id": "user123",
        "chat_id": chat_id,
        "message": "Chúng sống ở đâu?"
    }
)
result = response.json()
print(f"AI: {result['message']}")

# Upload ảnh + hỏi
with open("snake.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/chat/message",
        data={
            "user_id": "user123",
            "chat_id": chat_id,
            "message": "Con này có nguy hiểm không?"
        },
        files={"file": f}
    )
result = response.json()
print(f"Detected: {result.get('snake_detected')}")
print(f"AI: {result['message']}")
```

## 🎨 Frontend Integration (React/Next.js)

```typescript
// services/chatService.ts
export const sendMessage = async (
  userId: string,
  message: string,
  chatId?: string,
  file?: File
) => {
  const formData = new FormData();
  formData.append("user_id", userId);
  formData.append("message", message);
  if (chatId) formData.append("chat_id", chatId);
  if (file) formData.append("file", file);

  const response = await fetch("http://localhost:8000/api/chat/message", {
    method: "POST",
    body: formData,
  });

  return response.json();
};

// Component usage
const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [chatId, setChatId] = useState(null);

  const handleSend = async (message: string, file?: File) => {
    const result = await sendMessage("user123", message, chatId, file);
    
    if (!chatId) setChatId(result.chat_id);
    
    setMessages([
      ...messages,
      { role: "human", content: message },
      { role: "ai", content: result.message }
    ]);
  };

  return (
    // ... UI code
  );
};
```

## 🧪 Testing

```bash
# Test endpoint
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=test_user" \
  -F "message=Test message"

# Check MongoDB
mongo
use asksnake
db.chats.find().pretty()
```

## 🐛 Troubleshooting

1. **MongoDB connection failed**
   - Kiểm tra MONGO_URI trong .env
   - Đảm bảo MongoDB đang chạy

2. **RAG index not found**
   - Chạy ingest script trước: `python ingest.py`

3. **Import errors**
   - Cài đặt dependencies: `pip install -r requirements.txt`

## 📚 Tài liệu liên quan

- [MongoDB Motor Documentation](https://motor.readthedocs.io/)
- [LangChain Memory](https://python.langchain.com/docs/modules/memory/)
- [Qdrant Vector Store](https://qdrant.tech/documentation/)
- [Gemini LLM API](https://ai.google.dev/gemini-api/docs)

## 🎉 Features

- ✅ Persistent chat history
- ✅ Contextual responses với memory
- ✅ Automatic summarization
- ✅ Image + text queries
- ✅ Multi-user support
- ✅ Soft delete chats
- ✅ RAG với reranking
- ✅ Async MongoDB operations
