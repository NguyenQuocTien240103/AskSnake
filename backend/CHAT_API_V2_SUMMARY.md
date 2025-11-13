# 🎯 Chat API v2 - Implementation Summary

## ✅ Đã Triển Khai

### 📁 Files Created/Modified

1. **`pydantics/chat.py`** - Pydantic models
   - `Message`: Model cho một message
   - `Chat`: Model cho cuộc hội thoại
   - `ChatRequest`: Request schema
   - `ChatResponse`: Response schema

2. **`services/ChatService.py`** - MongoDB service
   - `create_chat()`: Tạo chat mới
   - `get_chat()`: Lấy thông tin chat
   - `add_message()`: Thêm message
   - `get_recent_messages()`: Lấy N messages gần nhất
   - `update_summary()`: Cập nhật summary
   - `get_chat_summary()`: Lấy summary
   - `get_message_count()`: Đếm messages
   - `list_user_chats()`: Danh sách chats
   - `delete_chat()`: Xóa mềm chat
   - `messages_to_langchain_format()`: Convert sang LangChain format

3. **`services/RagService.py`** - Updated
   - `query_with_history()`: Query RAG với chat history và summary

4. **`rag/llm.py`** - Updated
   - `generate_response_with_history()`: Generate với chat history
   - `generate_summary()`: Tạo summary cho cuộc hội thoại

5. **`routers/chat_router_v2.py`** - Main chat router
   - `POST /api/chat/message`: Gửi message (main endpoint)
   - `GET /api/chat/history/{chat_id}`: Lấy lịch sử
   - `GET /api/chat/list/{user_id}`: Danh sách chats
   - `DELETE /api/chat/{chat_id}`: Xóa chat
   - `POST /api/chat/regenerate-summary/{chat_id}`: Tạo lại summary

6. **`main.py`** - Updated
   - Thêm chat_router_v2

7. **`CHAT_API_V2_README.md`** - Documentation

8. **`test_chat_api.py`** - Test script

## 🔄 Luồng Hoạt Động Chi Tiết

### Main Chat Flow (`POST /api/chat/message`)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. REQUEST                                                   │
│    - user_id, message, chat_id (optional), file (optional)  │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. IMAGE PROCESSING (if file provided)                      │
│    - ImageService.detect_image()                            │
│    - Extract snake_name, probability                        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. CHAT MANAGEMENT                                          │
│    - Create new chat if chat_id is None                     │
│    - Or verify existing chat                                │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. SAVE USER MESSAGE → MongoDB                              │
│    - Role: "human"                                          │
│    - Content: message                                       │
│    - Metadata: {snake_detected, probability}                │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. FETCH CONTEXT                                            │
│    - Get 10 recent messages from MongoDB                    │
│    - Get summary (if exists)                                │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. RAG QUERY                                                │
│    ┌──────────────────────────────────────────┐            │
│    │ If snake_name exists:                    │            │
│    │   → query_with_image()                   │            │
│    │   → Specialized prompt for snake info    │            │
│    └──────────────────────────────────────────┘            │
│    ┌──────────────────────────────────────────┐            │
│    │ Else:                                     │            │
│    │   → query_with_history()                 │            │
│    │   → Generic query with chat history      │            │
│    └──────────────────────────────────────────┘            │
│                                                             │
│    Sub-steps:                                               │
│    a) Generate query embedding                              │
│    b) Search Qdrant for similar chunks (top K)              │
│    c) Apply reranking (if enabled)                          │
│    d) LLM generates response with:                          │
│       - Retrieved context                                   │
│       - Chat history (10 messages)                          │
│       - Summary (if exists)                                 │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. SAVE AI RESPONSE → MongoDB                               │
│    - Role: "ai"                                             │
│    - Content: ai_response                                   │
│    - Metadata: {context_chunks_used, reranking_used}        │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. AUTO-SUMMARY CHECK                                       │
│    - Count total messages in chat                           │
│    - If messages >= 20 AND no summary exists:               │
│      a) Fetch all messages                                  │
│      b) LLM.generate_summary(messages)                      │
│      c) Save summary to MongoDB                             │
└────────────────────────┬────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 9. RESPONSE                                                 │
│    {                                                        │
│      chat_id: string,                                       │
│      message: string,                                       │
│      context_used: int,                                     │
│      was_summarized: bool                                   │
│    }                                                        │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Component Integration

### LangChain Memory Integration

```python
# In RagService.query_with_history()
def query_with_history(
    self, 
    question: str, 
    chat_history: List[Dict],  # 10 messages gần nhất
    summary: Optional[str],     # Summary của toàn bộ chat
    top_k: int
):
    # 1. Retrieve context từ Qdrant (RAG)
    similar_texts = self.vector_store.search(query_embedding, top_k)
    
    # 2. Generate response với context + history
    response = self.llm.generate_response_with_history(
        query=question,
        context=similar_texts,      # From Qdrant
        chat_history=chat_history,  # Recent 10 messages
        summary=summary             # Summary of earlier messages
    )
```

### MongoDB Integration

```python
# Collection structure
chats_collection = db.get_collection("chats")

# Document structure
{
  "_id": ObjectId,
  "user_id": str,
  "title": str,
  "messages": [
    {
      "role": "human" | "ai" | "system",
      "content": str,
      "timestamp": datetime,
      "metadata": dict
    }
  ],
  "summary": str | null,
  "created_at": datetime,
  "updated_at": datetime,
  "is_active": bool
}
```

### RAG Integration

```python
# RAG Pipeline
Query → Embedding → Qdrant Search → Reranking → LLM

# With memory
Query + History + Summary → [Same RAG Pipeline] → Response
```

## 🔧 Configuration

### Environment Variables (`.env`)
```env
# MongoDB
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=asksnake

# Google AI
GOOGLE_API_KEY=your_key

# Qdrant
QDRANT_URL=your_url
QDRANT_API_KEY=your_key
```

### Tunable Parameters

In `chat_router_v2.py`:
```python
MAX_MESSAGES_BEFORE_SUMMARY = 20  # Auto-summarize threshold
RECENT_MESSAGES_COUNT = 10        # Number of messages for context
```

In `rag_config.py`:
```python
TOP_K_RESULTS = 5           # Number of context chunks
USE_RERANKING = True        # Enable reranking
RERANK_TOP_K = 10           # Initial retrieval
FINAL_TOP_K = 5             # After reranking
```

## 📊 Performance Optimization

### Database Indexes (MongoDB)

```javascript
// Create indexes for performance
db.chats.createIndex({ "user_id": 1, "is_active": 1 })
db.chats.createIndex({ "updated_at": -1 })
db.chats.createIndex({ "user_id": 1, "updated_at": -1 })
```

### Memory Management

- **Recent Messages**: Only keep last 10 in context
- **Summary**: Compress older messages into summary
- **Lazy Loading**: Load messages on-demand, not all at once

### Caching Strategies (Future)

```python
# Can add Redis caching for:
- Recent messages
- Summaries
- Frequently accessed chats
```

## 🧪 Testing

### Run Test Script
```bash
cd backend
python test_chat_api.py
```

### Manual Testing with cURL
```bash
# Create new chat
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=test_user" \
  -F "message=Rắn hổ mang có độc không?"

# Continue chat
curl -X POST http://localhost:8000/api/chat/message \
  -F "user_id=test_user" \
  -F "chat_id=<chat_id_from_above>" \
  -F "message=Chúng sống ở đâu?"

# Get history
curl http://localhost:8000/api/chat/history/<chat_id>

# List chats
curl http://localhost:8000/api/chat/list/test_user
```

## 🚀 Deployment Checklist

- [ ] MongoDB instance running and accessible
- [ ] Qdrant vector store initialized with data
- [ ] Environment variables configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Database indexes created
- [ ] API endpoints tested
- [ ] Error handling verified
- [ ] Rate limiting configured (if needed)
- [ ] CORS settings adjusted for frontend domain

## 🎨 Frontend Integration Guide

### Next.js / React Example

```typescript
// types/chat.ts
interface Message {
  role: 'human' | 'ai';
  content: string;
  timestamp: string;
}

interface Chat {
  chat_id: string;
  title: string;
  messages: Message[];
}

// hooks/useChat.ts
export const useChat = (userId: string) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<string | null>(null);
  
  const sendMessage = async (message: string, file?: File) => {
    const formData = new FormData();
    formData.append('user_id', userId);
    formData.append('message', message);
    if (currentChat) formData.append('chat_id', currentChat);
    if (file) formData.append('file', file);
    
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      body: formData,
    });
    
    const result = await response.json();
    if (!currentChat) setCurrentChat(result.chat_id);
    
    return result;
  };
  
  return { chats, currentChat, sendMessage };
};
```

## 📈 Monitoring & Logs

### Key Metrics to Track
- Average response time
- Context chunks used per query
- Summary generation frequency
- Message count distribution
- Error rates

### Logging Points
```python
# Already implemented in code:
- Image detection results
- Message save operations
- RAG query performance
- Summary generation
- Error stack traces
```

## 🔒 Security Considerations

### Current Implementation
- ✅ User ID validation
- ✅ Chat ownership (user_id in document)
- ✅ Soft delete (preserves data)

### Recommended Additions
- [ ] JWT authentication
- [ ] Rate limiting per user
- [ ] Input sanitization
- [ ] File upload validation
- [ ] Chat access control

## 📚 References

- MongoDB Motor: https://motor.readthedocs.io/
- LangChain: https://python.langchain.com/
- Qdrant: https://qdrant.tech/
- Gemini API: https://ai.google.dev/

## 🎉 Next Steps

1. **Test in staging environment**
2. **Monitor performance**
3. **Gather user feedback**
4. **Optimize based on usage patterns**
5. **Add more features**:
   - Export chat history
   - Search within chats
   - Share chats
   - Voice input/output
   - Multi-language support

---

**Created**: 2024-11-13
**Version**: 2.0.0
**Status**: ✅ Ready for Testing
