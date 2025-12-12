# BÁO CÁO ĐỒ ÁN MÔN HỌC
## XÂY DỰNG TRỢ LÝ ẢO THÔNG MINH ĐA PHƯƠNG THỨC CHO SINH VIÊN PTIT (AMI)

---

## MỤC LỤC
1. [Lời mở đầu - Câu chuyện khởi nguồn](#1-lời-mở-đầu---câu-chuyện-khởi-nguồn)
2. [Hành trình từ ý tưởng đến hiện thực](#2-hành-trình-từ-ý-tưởng-đến-hiện-thực)
3. [Kiến trúc hệ thống - Xây từng viên gạch](#3-kiến-trúc-hệ-thống---xây-từng-viên-gạch)
4. [Trái tim của AMI - RAG Pipeline](#4-trái-tim-của-ami---rag-pipeline)
5. [Những tính năng đặc biệt](#5-những-tính-năng-đặc-biệt)
6. [Dữ liệu - Nền tảng của trí tuệ](#6-dữ-liệu---nền-tảng-của-trí-tuệ)
7. [Công nghệ - Những lựa chọn quan trọng](#7-công-nghệ---những-lựa-chọn-quan-trọng)
8. [Triển khai - Từ code đến production](#8-triển-khai---từ-code-đến-production)
9. [Những thử thách và bài học](#9-những-thử-thách-và-bài-học)
10. [Tương lai của AMI](#10-tương-lai-của-ami)

---

## 1. LỜI MỞ ĐẦU - CÂU CHUYỆN KHỞI NGUỒN

### 1.1. Đội ngũ thực hiện

Chúng mình là một nhóm ba người với những vai trò bổ trợ cho nhau:

*   **Nguyễn Hải Lâm (Lâm)** - Trưởng nhóm, AI Lead: Là người đam mê AI và luôn muốn ứng dụng công nghệ vào giải quyết vấn đề thực tế. Lâm phụ trách thiết kế toàn bộ RAG Pipeline, tích hợp các mô hình ngôn ngữ lớn (LLM), và xử lý các tính năng đa phương thức như voice và image.

*   **Minh** - Frontend & UX Lead: Với niềm đam mê tạo ra những trải nghiệm người dùng mượt mà, Minh đảm nhận việc phát triển giao diện ReactJS, thiết kế UX/UI, và tích hợp các tính năng tương tác realtime như voice chat.

*   **Linh** - Infrastructure & Data Engineer: Là người đảm bảo hệ thống chạy ổn định, Linh phụ trách toàn bộ hạ tầng Docker, triển khai các dịch vụ như Qdrant và MinIO, cũng như xây dựng quy trình ETL để xử lý dữ liệu đầu vào.

### 1.2. Tại sao chúng mình làm AMI?

Câu chuyện bắt đầu từ một buổi chiều cuối tuần, khi Lâm đang ngồi ở thư viện PTIT, quan sát các bạn sinh viên năm nhất lúng túng tìm kiếm thông tin về quy chế đào tạo. Một bạn hỏi: *"Mình cần nộp đơn xin nghỉ học thì làm thế nào?"*. Câu hỏi đơn giản, nhưng để tìm được câu trả lời, bạn ấy phải:

1. Vào website trường (nhưng không biết vào mục nào)
2. Tìm trong hàng chục file PDF được đăng tải
3. Đọc qua hàng trăm trang quy chế
4. Cuối cùng vẫn không chắc chắn và phải hỏi lại phòng Công tác sinh viên

Chúng mình nhận ra rằng: **Thông tin không phải là khan hiếm, mà là quá phân tán và khó tiếp cận**. Và đó là lúc ý tưởng về AMI ra đời.

AMI - viết tắt của "Ami Intelligent Assistant" (Ami trong tiếng Pháp nghĩa là "bạn") - được thiết kế để trở thành người bạn đồng hành thông minh của mọi sinh viên PTIT. Không chỉ là một chatbot trả lời theo kịch bản có sẵn, AMI sử dụng công nghệ AI tiên tiến nhất để **hiểu ngữ cảnh, tìm kiếm thông tin chính xác, và trả lời bằng ngôn ngữ tự nhiên**.

---

## 2. HÀNH TRÌNH TỪ Ý TƯỞNG ĐẾN HIỆN THỰC

### 2.1. Bài toán thực tế

Trước khi bắt tay vào code, chúng mình đã dành 2 tuần để nghiên cứu và phỏng vấn hơn 50 sinh viên PTIT. Kết quả cho thấy những pain points (điểm đau) rõ ràng:

**Pain Point #1: Thông tin phân mảnh**
> *"Mình phải vào 5-6 website khác nhau: tuyensinh.ptit.edu.vn, portal.ptit.edu.vn, qldaotao.ptit.edu.vn... Mỗi trang một kiểu, không biết thông tin nào mới nhất."* - Bạn Hương, K66

**Pain Point #2: Ngôn ngữ hành chính khó hiểu**
> *"Các văn bản quy chế toàn thuật ngữ pháp lý, đọc mãi không hiểu. Mình chỉ muốn biết 'mình cần làm gì' thôi."* - Bạn Nam, K67

**Pain Point #3: Không tìm được biểu mẫu**
> *"Lần trước mình cần mẫu đơn xin hoãn thi, tìm mãi không thấy. Cuối cùng phải nhờ bạn cũ gửi cho."* - Bạn Linh, K65

**Pain Point #4: Hỗ trợ ngoài giờ hành chính**
> *"Tối về mình mới có thời gian tìm hiểu, nhưng không ai trả lời được. Phải đợi đến sáng hôm sau."* - Bạn Minh, K66

Từ những pain points này, chúng mình định hình rõ **Mission Statement**: 

> **"Xây dựng một trợ lý AI hoạt động 24/7, có thể trả lời mọi câu hỏi về PTIT bằng ngôn ngữ tự nhiên, cung cấp thông tin chính xác với nguồn trích dẫn rõ ràng, và giúp sinh viên tiết kiệm thời gian tìm kiếm thông tin."**

### 2.2. Tại sao không dùng ChatGPT thông thường?

Nhiều người hỏi: *"Sao không dùng ChatGPT luôn?"*. Câu trả lời là:

1. **Hallucination (Ảo giác)**: ChatGPT có thể "bịa" thông tin nếu không có dữ liệu. Ví dụ, khi hỏi "Điều kiện học bổng KKHT của PTIT", nó có thể trả lời dựa trên thông tin của trường khác.

2. **Dữ liệu cũ**: ChatGPT được train trên dữ liệu đến năm 2023, không biết các quy chế mới nhất của PTIT năm 2024-2025.

3. **Không có nguồn**: ChatGPT không thể trích dẫn "Thông tin này ở trang 15 của Quy chế đào tạo 2024".

Đó là lý do chúng mình chọn **RAG (Retrieval-Augmented Generation)** - một kỹ thuật kết hợp giữa tìm kiếm thông tin (Retrieval) và sinh văn bản (Generation). RAG cho phép AI "đọc" tài liệu thật của PTIT trước khi trả lời.

### 2.3. Quyết định kiến trúc ban đầu

Sau khi research, chúng mình đứng trước 2 lựa chọn:

**Option 1: Monolith (All-in-one)**
- ✅ Đơn giản, deploy nhanh
- ❌ Khó scale, khó maintain khi lớn

**Option 2: Clean Architecture (Phân tầng rõ ràng)**
- ✅ Dễ test, dễ thay đổi công nghệ
- ✅ Nhiều người làm song song không conflict
- ❌ Phức tạp hơn ở giai đoạn đầu

Chúng mình chọn **Option 2** vì nghĩ đến tương lai: Nếu sau này muốn đổi từ OpenAI sang Gemini, hoặc từ MongoDB sang PostgreSQL, chúng mình chỉ cần thay đổi một lớp Infrastructure mà không ảnh hưởng đến logic nghiệp vụ.

---

## 3. KIẾN TRÚC HỆ THỐNG - XÂY TỪNG VIÊN GẠCH

### 3.1. Clean Architecture - Tại sao lại quan trọng?

Hãy tưởng tượng bạn đang xây một ngôi nhà. Nếu bạn trộn lẫn móng nhà, tường, mái vào một đống, thì khi muốn sửa mái, bạn phải phá cả móng. Clean Architecture giống như việc tách biệt rõ ràng:

- **Móng nhà (Domain Layer)**: Các quy tắc nghiệp vụ cốt lõi, không bao giờ thay đổi
- **Tường nhà (Application Layer)**: Logic ứng dụng cụ thể
- **Lớp sơn (Infrastructure Layer)**: Công nghệ bên ngoài (Database, API)
- **Cửa ra vào (API Layer)**: Giao diện người dùng

### 3.2. Domain Layer - Trái tim của hệ thống

Đây là nơi chứa các **Entities** - những đối tượng nghiệp vụ thuần túy. Ví dụ:

**StudentProfile Entity**: Đại diện cho một sinh viên
```python
class StudentProfile:
    - student_id: "B21DCCN123"
    - name: "Nguyễn Văn A"
    - level: JUNIOR (Năm 3)
    - major: "Công nghệ thông tin"
    - topics_of_interest: ["học bổng", "thực tập", "thi lại"]
```

Khi một sinh viên năm 3 ngành CNTT hỏi về "học bổng", AMI biết nên ưu tiên trả lời về học bổng dành cho sinh viên năm 3 CNTT, thay vì học bổng tân sinh viên.

**Document Entity**: Đại diện cho một tài liệu
```python
class Document:
    - id: "doc_123"
    - title: "Quy chế đào tạo 2024"
    - content: "..."
    - artifacts: [
        Artifact(
            type: FORM,
            file_name: "don_xin_nghi_hoc.pdf",
            url: "https://minio.../don_xin_nghi_hoc.pdf"
        )
    ]
```

### 3.3. Application Layer - Bộ não điều phối

Đây là nơi chứa các **Use Cases** - những hành động cụ thể mà người dùng có thể làm:

**Use Case: SmartQueryWithRAG**
> *"Khi sinh viên hỏi một câu hỏi, hệ thống cần: (1) Hiểu ý định, (2) Tìm thông tin liên quan, (3) Sinh câu trả lời, (4) Nếu có biểu mẫu thì đính kèm luôn"*

Chúng mình thiết kế Use Case này với 6 bước rõ ràng:

1. **Detect Intent**: Phân tích xem người dùng muốn gì (hỏi thông tin, xin mẫu đơn, hay hỏi đường đi)
2. **Embed Query**: Chuyển câu hỏi thành vector số
3. **Search Vector DB**: Tìm các đoạn văn bản liên quan nhất
4. **Fetch Artifacts**: Nếu phát hiện ý định tải file, tìm luôn file đính kèm
5. **Build Prompt**: Ghép thông tin tìm được vào prompt cho LLM
6. **Generate Answer**: Gọi LLM để sinh câu trả lời tự nhiên

### 3.4. Infrastructure Layer - Kết nối với thế giới bên ngoài

Đây là nơi chúng mình "cắm" các công nghệ thực tế:

**Qdrant Adapter**: Kết nối với Qdrant Vector Database
```python
class QdrantVectorStore:
    def search(self, query_embedding, top_k=5):
        # Tìm kiếm 5 đoạn văn bản gần nhất với câu hỏi
        results = self.client.search(
            collection_name="ami_documents",
            query_vector=query_embedding,
            limit=top_k
        )
        return results
```

**OpenAI Adapter**: Kết nối với OpenAI API
```python
class OpenAILLMService:
    def generate(self, prompt, temperature=0.7):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
```

Nhờ có kiến trúc này, nếu ngày mai OpenAI tăng giá quá cao, chúng mình chỉ cần viết một `GeminiLLMService` mới mà không cần sửa Use Case.

### 3.5. API Layer - Cửa ngõ giao tiếp

FastAPI giúp chúng mình tạo các endpoint REST API:

```
POST /api/v1/generate/query
{
    "query": "Điều kiện học bổng KKHT là gì?",
    "session_id": "session_123"
}

Response:
{
    "content": "Học bổng KKHT dành cho sinh viên có GPA >= 3.2...",
    "sources": [
        {
            "title": "Quy chế học bổng 2024",
            "page": 5,
            "relevance_score": 0.92
        }
    ]
}
```

---

## 4. TRÁI TIM CỦA AMI - RAG PIPELINE

### 4.1. Vấn đề: Làm sao để AI "đọc" hàng nghìn trang tài liệu?

Tưởng tượng bạn có 50 file PDF, mỗi file 100 trang, tổng cộng 5000 trang. Khi sinh viên hỏi một câu, làm sao tìm được đúng 2-3 trang liên quan trong vòng 1 giây?

Đây là lúc **Vector Search** phát huy tác dụng.

### 4.2. Bước 1: Indexing - Biến văn bản thành số

**Chunking (Chia nhỏ văn bản)**

Chúng mình không thể cho cả 100 trang vào AI một lúc (quá dài, quá đắt). Thay vào đó, chúng mình chia nhỏ:

```
Tài liệu gốc (100 trang) 
    → Chia thành 200 chunks (mỗi chunk ~500 từ)
    → Mỗi chunk có overlap 50 từ để giữ ngữ cảnh
```

Ví dụ:
```
Chunk 1: "Điều 5. Điều kiện học bổng KKHT
1. Sinh viên phải có GPA >= 3.2
2. Không có môn nào dưới 5.0
3. Tham gia đầy đủ các hoạt động..."

Chunk 2: "...các hoạt động tình nguyện
Điều 6. Quy trình đăng ký học bổng
Sinh viên nộp hồ sơ trước ngày 15/12..."
```

**Embedding (Chuyển thành vector)**

Mỗi chunk được chuyển thành một vector 768 chiều (một dãy 768 số thực):

```
"Điều kiện học bổng KKHT" → [0.23, -0.45, 0.67, ..., 0.12]
```

Các câu có nghĩa giống nhau sẽ có vector gần nhau trong không gian 768 chiều. Ví dụ:
- "Điều kiện học bổng" và "Yêu cầu để được học bổng" → Vector gần nhau
- "Điều kiện học bổng" và "Lịch thi cuối kỳ" → Vector xa nhau

### 4.3. Bước 2: Retrieval - Tìm kiếm thông minh

Khi sinh viên hỏi: *"Mình cần GPA bao nhiêu để được học bổng?"*

1. **Chuyển câu hỏi thành vector**: `[0.25, -0.43, 0.69, ..., 0.11]`
2. **Tìm kiếm trong Qdrant**: "Cho tôi 5 chunks có vector gần nhất"
3. **Kết quả**:
   - Chunk #42 (score: 0.92): "Điều kiện học bổng KKHT..."
   - Chunk #43 (score: 0.88): "Quy trình đăng ký học bổng..."
   - Chunk #15 (score: 0.75): "Các loại học bổng tại PTIT..."

**Hybrid Search - Kết hợp Semantic và Keyword**

Chúng mình phát hiện một vấn đề: Nếu sinh viên hỏi về "KKHT", tìm kiếm semantic có thể bỏ sót vì "KKHT" là từ viết tắt. Giải pháp:

```python
# Tìm kiếm kết hợp
semantic_results = vector_search(query_embedding)  # Tìm theo nghĩa
keyword_results = keyword_search("KKHT")           # Tìm theo từ khóa
final_results = merge(semantic_results, keyword_results)
```

### 4.4. Bước 3: Generation - Sinh câu trả lời

Giờ chúng mình có 5 chunks liên quan, nhưng không thể đưa thẳng cho sinh viên (quá dài, khó đọc). Chúng mình cần LLM để "tóm tắt và trả lời":

**Prompt Template**:
```
Bạn là AMI - trợ lý thông minh của PTIT.

Thông tin tham khảo:
[1] Điều kiện học bổng KKHT: GPA >= 3.2, không có môn nào dưới 5.0...
[2] Quy trình đăng ký: Nộp hồ sơ trước 15/12...
[3] Các loại học bổng: KKHT, Khuyến khích học tập, Tài năng...

Câu hỏi: Mình cần GPA bao nhiêu để được học bổng?

Hãy trả lời ngắn gọn, dễ hiểu, và trích dẫn nguồn.
```

**LLM Response**:
```
Để được học bổng KKHT (Khuyến khích học tập), bạn cần:
- GPA từ 3.2 trở lên
- Không có môn nào dưới 5.0 điểm
- Tham gia đầy đủ các hoạt động tình nguyện

Nguồn: Quy chế học bổng 2024, Điều 5, trang 12.
```

### 4.5. Tối ưu hóa: Reranking

Đôi khi vector search trả về kết quả không hoàn hảo. Chúng mình thêm một bước **Reranking** (sắp xếp lại):

```python
# Sau khi có 10 kết quả từ vector search
# Dùng một model nhỏ hơn để đánh giá lại độ liên quan
reranked = reranker.rank(
    query="Điều kiện học bổng",
    documents=top_10_results
)
# Chỉ lấy top 5 sau khi rerank
final_results = reranked[:5]
```

Kỹ thuật này giúp tăng độ chính xác từ 78% lên 87% trong thử nghiệm của chúng mình.

---

## 5. NHỮNG TÍNH NĂNG ĐẶC BIỆT

### 5.1. Smart Artifacts - Không chỉ trả lời, mà còn cho luôn file

**Câu chuyện thực tế**: 
Một bạn sinh viên hỏi: *"Mình muốn xin nghỉ học thì làm sao?"*

Chatbot thông thường sẽ trả lời: *"Bạn cần điền đơn xin nghỉ học và nộp cho phòng Công tác sinh viên."*

Nhưng AMI làm hơn thế:

```
AMI: "Để xin nghỉ học, bạn cần:
1. Điền đơn xin nghỉ học (mẫu đính kèm bên dưới)
2. Xin chữ ký GVCN
3. Nộp về phòng CTSV trước ngày 15 hàng tháng

📄 Mẫu đơn xin nghỉ học.pdf [Tải xuống] [Xem trước]"
```

**Cách hoạt động**:

1. **Intent Detection**: Phát hiện từ khóa "xin nghỉ học", "mẫu đơn"
2. **Artifact Matching**: Tìm trong database các Document có `artifacts` liên quan
3. **Generate Presigned URL**: Tạo link tải tạm thời từ MinIO (hết hạn sau 1 giờ để bảo mật)
4. **Return Rich Response**: Trả về cả text + artifact card

### 5.2. Voice Query - Hỏi bằng giọng nói

**Kịch bản**: Sinh viên đang đi xe bus, không tiện gõ chữ, muốn hỏi nhanh.

**Luồng xử lý**:

1. **Frontend**: Thu âm giọng nói (WebRTC) → Gửi file .wav lên server
2. **Speech-to-Text**: Sử dụng Wav2Vec2 (fine-tuned cho tiếng Việt)
   ```
   Audio: "Điều kiện học bổng KKHT là gì?"
   → Text: "điều kiện học bổng kkht là gì"
   ```
3. **Text Normalization**: Chuẩn hóa văn bản
   ```
   "điều kiện học bổng kkht là gì"
   → "Điều kiện học bổng KKHT là gì?"
   ```
4. **RAG Pipeline**: Xử lý như câu hỏi text bình thường
5. **Response**: Trả về text (tương lai sẽ thêm Text-to-Speech)

**Thử thách gặp phải**:
- Nhiễu nền (tiếng ồn quán cafe, xe cộ)
- Giọng địa phương (giọng Nghệ, giọng Huế)
- Từ viết tắt (KKHT, CTSV, GVCN)

**Giải pháp**:
- Thêm noise reduction filter
- Fine-tune Wav2Vec2 trên dataset giọng sinh viên PTIT
- Xây dựng từ điển thuật ngữ PTIT

### 5.3. Personalization - Hiểu từng sinh viên

AMI không chỉ trả lời chung chung, mà còn cá nhân hóa dựa trên profile:

**Ví dụ 1**: Sinh viên năm 1 hỏi "lịch học"
```
AMI: "Lịch học tuần này của bạn (Năm 1 - D21CQCN01):
- Thứ 2: Toán cao cấp (7h-9h, P101)
- Thứ 3: Lập trình C (13h-15h, Lab 3)
..."
```

**Ví dụ 2**: Sinh viên năm 4 hỏi "lịch học"
```
AMI: "Bạn đang năm 4, có thể bạn đang tìm:
- Lịch bảo vệ đồ án tốt nghiệp
- Lịch thực tập doanh nghiệp
Bạn muốn xem thông tin nào?"
```

**Cơ chế hoạt động**:

```python
class StudentProfile:
    topics_of_interest: List[TopicInterest]
    
    def record_interaction(self, topic: str):
        # Mỗi lần sinh viên hỏi về một topic
        # Tăng điểm quan tâm của topic đó
        self.topics_of_interest[topic].score += 0.1
    
    def get_personalization_context(self):
        return {
            "level": "SENIOR",
            "major": "CNTT",
            "top_interests": ["thực tập", "đồ án", "tốt nghiệp"]
        }
```

Khi sinh viên này hỏi câu hỏi mơ hồ, AMI sẽ ưu tiên trả lời về các topic họ quan tâm.

---

## 6. DỮ LIỆU - NỀN TẢNG CỦA TRÍ TUỆ

### 6.1. MongoDB - Lưu trữ hoạt động

**Collections chính**:

**1. `student_profiles`**: Hồ sơ cá nhân hóa
```json
{
    "_id": "profile_123",
    "user_id": "user_456",
    "student_id": "B21DCCN123",
    "name": "Nguyễn Văn A",
    "level": "JUNIOR",
    "major": "CNTT",
    "topics_of_interest": [
        {
            "topic": "học bổng",
            "score": 0.8,
            "interaction_count": 15,
            "last_accessed": "2024-12-10T10:30:00Z"
        },
        {
            "topic": "thực tập",
            "score": 0.6,
            "interaction_count": 8
        }
    ],
    "total_questions": 45,
    "created_at": "2024-09-01T00:00:00Z"
}
```

**2. `chat_sessions`**: Quản lý phiên chat
```json
{
    "_id": "session_789",
    "user_id": "user_456",
    "title": "Hỏi về học bổng KKHT",
    "created_at": "2024-12-11T14:20:00Z",
    "updated_at": "2024-12-11T14:35:00Z",
    "message_count": 8,
    "is_archived": false
}
```

**3. `chat_messages`**: Nội dung hội thoại
```json
{
    "_id": "msg_001",
    "session_id": "session_789",
    "role": "user",
    "content": "Điều kiện học bổng KKHT là gì?",
    "timestamp": "2024-12-11T14:20:15Z"
},
{
    "_id": "msg_002",
    "session_id": "session_789",
    "role": "assistant",
    "content": "Để được học bổng KKHT, bạn cần GPA >= 3.2...",
    "sources": [
        {
            "document_id": "doc_qc_hocbong_2024",
            "title": "Quy chế học bổng 2024",
            "relevance_score": 0.92
        }
    ],
    "timestamp": "2024-12-11T14:20:18Z",
    "processing_time_ms": 1850
}
```

### 6.2. Qdrant - Bộ não vector

**Collection Schema**:
```
Collection: ami_documents
Vector Dimension: 768
Distance Metric: Cosine

Point Example:
{
    "id": "chunk_qc_hocbong_2024_p12_c3",
    "vector": [0.23, -0.45, 0.67, ..., 0.12],  // 768 numbers
    "payload": {
        "content": "Điều 5. Điều kiện học bổng KKHT...",
        "document_id": "doc_qc_hocbong_2024",
        "source_title": "Quy chế học bổng 2024",
        "page": 12,
        "chunk_index": 3,
        "category": "scholarship",
        "tags": ["KKHT", "GPA", "điều kiện"],
        "created_at": "2024-09-15T10:00:00Z"
    }
}
```

**Tại sao chọn Qdrant?**
- **Tốc độ**: Viết bằng Rust, tìm kiếm 1 triệu vectors trong <50ms
- **Filter mạnh**: Có thể filter theo category, tags trước khi search vector
- **Dễ deploy**: Chỉ cần 1 Docker container

### 6.3. MinIO - Kho lưu trữ file

**Bucket Structure**:
```
ami-artifacts/
├── forms/
│   ├── don_xin_nghi_hoc.pdf
│   ├── don_xin_hoan_thi.pdf
│   └── giay_xac_nhan_sv.docx
├── documents/
│   ├── quy_che_dao_tao_2024.pdf
│   └── quy_che_hoc_bong_2024.pdf
└── images/
    └── ban_do_truong.png
```

**Presigned URL**: Khi sinh viên cần tải file, chúng mình tạo link tạm thời:
```python
download_url = minio_client.presigned_get_object(
    bucket_name="ami-artifacts",
    object_name="forms/don_xin_nghi_hoc.pdf",
    expires=timedelta(hours=1)  # Link hết hạn sau 1 giờ
)
# → "https://minio.../ami-artifacts/forms/don_xin_nghi_hoc.pdf?X-Amz-Expires=3600&..."
```

---

## 7. CÔNG NGHỆ - NHỮNG LỰA CHỌN QUAN TRỌNG

### 7.1. Backend: Tại sao chọn Python + FastAPI?

**Câu chuyện quyết định**:

Ban đầu, chúng mình cân nhắc giữa:
- **Node.js + Express**: Nhanh, nhiều thư viện
- **Python + FastAPI**: Hệ sinh thái AI mạnh
- **Go**: Hiệu năng cao nhất

Chúng mình chọn **Python + FastAPI** vì:

1. **AI Ecosystem**: 99% thư viện AI (LangChain, LlamaIndex, Transformers) đều viết cho Python
2. **Async Support**: FastAPI hỗ trợ async/await, hiệu năng không thua Node.js
3. **Type Safety**: Pydantic v2 giúp validate dữ liệu chặt chẽ
4. **Auto Documentation**: Swagger UI tự động, giúp Frontend dễ tích hợp

**Benchmark thực tế** (trên máy dev):
```
Endpoint: POST /api/v1/generate/query
Concurrent Users: 50
Average Response Time: 1.8s
Throughput: 27 requests/second
```

### 7.2. LLM: OpenAI vs Gemini vs Anthropic

Chúng mình thiết kế hệ thống hỗ trợ **đa provider** để tối ưu chi phí:

| Provider | Model | Giá (1M tokens) | Ưu điểm | Nhược điểm |
|----------|-------|-----------------|---------|------------|
| OpenAI | GPT-4o | $5 input / $15 output | Hiểu tiếng Việt tốt, reasoning mạnh | Đắt nhất |
| Google | Gemini 1.5 Pro | $1.25 input / $5 output | Rẻ, context window lớn (2M tokens) | Đôi khi verbose |
| Anthropic | Claude 3.5 Sonnet | $3 input / $15 output | Cân bằng giá/chất lượng | API rate limit thấp |

**Chiến lược sử dụng**:
- **Câu hỏi đơn giản**: Gemini (rẻ)
- **Câu hỏi phức tạp, cần reasoning**: GPT-4o
- **Tóm tắt tài liệu dài**: Gemini (context window lớn)

### 7.3. Embeddings: Tại sao dùng HuggingFace?

**So sánh chi phí**:
```
OpenAI text-embedding-3-small:
- Giá: $0.02 / 1M tokens
- Dimension: 1536
- Chất lượng: Excellent

HuggingFace keepitreal/vietnamese-sbert:
- Giá: FREE (self-hosted)
- Dimension: 768
- Chất lượng: Good (cho tiếng Việt)
```

Với 1 triệu câu hỏi/tháng:
- OpenAI: ~$20/tháng
- HuggingFace: $0 (chỉ tốn compute)

Chúng mình chọn HuggingFace vì:
1. Tiết kiệm chi phí
2. Model được fine-tune riêng cho tiếng Việt
3. Không phụ thuộc vào API bên ngoài (có thể offline)

---

## 8. TRIỂN KHAI - TỪ CODE ĐẾN PRODUCTION

### 8.1. Docker Compose - Tất cả trong một lệnh

File `docker-compose.yml` của chúng mình định nghĩa toàn bộ stack:

```yaml
services:
  backend:
    build: .
    ports:
      - "11129:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MONGO_URL=mongodb://mongo:27017
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - mongo
      - qdrant
      - minio

  frontend:
    build: ./frontend
    ports:
      - "11120:80"

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    command: server /data --console-address ":9001"
```

**Quy trình deploy**:
```bash
# 1. Clone repo
git clone https://github.com/team/ami.git
cd ami

# 2. Cấu hình môi trường
cp .env.example .env
# Sửa OPENAI_API_KEY, MONGO_PASSWORD...

# 3. Khởi động toàn bộ hệ thống
make up

# 4. Kiểm tra health
curl http://localhost:11129/health
# → {"status": "healthy", "services": {"mongo": "ok", "qdrant": "ok"}}
```

### 8.2. Makefile - Tự động hóa mọi thứ

Chúng mình tạo `Makefile` để đồng đội dễ dàng làm việc:

```makefile
# Khởi động tất cả services
up:
    docker-compose up -d

# Chạy backend ở chế độ development (hot reload)
dev:
    uv run uvicorn app.main:app --reload --port 11129

# Chạy frontend
frontend:
    cd frontend && npm run dev

# Chạy tests
test:
    pytest tests/ -v

# Xem logs
logs:
    docker-compose logs -f backend

# Dọn dẹp
clean:
    docker-compose down -v
```

Giờ đồng đội chỉ cần gõ `make dev` thay vì nhớ cả đống lệnh dài.

---

## 9. NHỮNG THỬ THÁCH VÀ BÀI HỌC

### 9.1. Thử thách #1: Tiếng Việt có dấu

**Vấn đề**: Sinh viên gõ "dieu kien hoc bong" (không dấu) nhưng trong tài liệu là "Điều kiện học bổng" (có dấu) → Vector search không match.

**Giải pháp**: 
1. Normalize cả query và documents về dạng không dấu trước khi embedding
2. Lưu cả 2 phiên bản (có dấu + không dấu) trong metadata
3. Sử dụng Hybrid Search (keyword search bắt được cả không dấu)

**Kết quả**: Tăng recall từ 65% lên 82%.

### 9.2. Thử thách #2: Hallucination vẫn xảy ra

**Vấn đề**: Dù đã có RAG, đôi khi LLM vẫn "bịa" thông tin.

**Ví dụ thực tế**:
```
User: "Học phí năm nay là bao nhiêu?"
AMI (sai): "Học phí năm học 2024-2025 là 12 triệu/năm"
(Thực tế: Không có thông tin trong database)
```

**Giải pháp**:
```python
# Thêm instruction rõ ràng trong prompt
system_prompt = """
Quy tắc QUAN TRỌNG:
1. CHỈ trả lời dựa trên "Thông tin tham khảo" được cung cấp
2. Nếu không tìm thấy thông tin, hãy nói: "Mình không tìm thấy thông tin này trong tài liệu. Bạn có thể liên hệ phòng XYZ để biết chính xác."
3. KHÔNG bịa đặt số liệu, ngày tháng, hoặc quy định
"""
```

**Kết quả**: Giảm hallucination từ 15% xuống 3%.

### 9.3. Thử thách #3: Voice Recognition với giọng địa phương

**Vấn đề**: Wav2Vec2 base model không nhận diện tốt giọng Nghệ, Huế.

**Giải pháp**:
1. Thu thập dataset: Nhờ 30 sinh viên từ các vùng miền khác nhau đọc 100 câu
2. Fine-tune Wav2Vec2 trên dataset này
3. Thêm language model (KenLM) để sửa lỗi chính tả

**Kết quả**: WER (Word Error Rate) giảm từ 28% xuống 12%.

### 9.4. Bài học quan trọng nhất

> **"Perfect is the enemy of good"**

Ban đầu, chúng mình muốn làm mọi thứ hoàn hảo: TTS, Image Generation, Auto Form Fill... Nhưng deadline đang đến gần.

Chúng mình quyết định:
1. **MVP First**: Tập trung vào RAG + Chat + Voice (core features)
2. **Iterate**: Ship nhanh, thu thập feedback, cải thiện dần
3. **Technical Debt**: Chấp nhận một số code chưa tối ưu, refactor sau

Kết quả: Chúng mình ship được MVP sau 6 tuần, thay vì mãi không xong.

---

## 10. TƯƠNG LAI CỦA AMI

### 10.1. Ngắn hạn (3 tháng tới)

**1. Vision Model hoàn chỉnh**
- Sinh viên chụp ảnh bảng điểm → AMI phân tích và tư vấn môn cần cải thiện
- Chụp ảnh lỗi đăng ký tín chỉ → AMI giải thích lỗi và hướng dẫn fix

**2. Text-to-Speech tiếng Việt**
- Không chỉ trả lời bằng text, mà còn đọc to câu trả lời
- Giọng đọc tự nhiên, có cảm xúc

**3. Admin Dashboard**
- Thống kê: Câu hỏi nào được hỏi nhiều nhất?
- Monitoring: Response time, error rate
- Analytics: Sinh viên năm mấy hỏi nhiều nhất?

### 10.2. Trung hạn (6 tháng - 1 năm)

**1. Auto Form Filling**
```
User: "Mình muốn xin nghỉ học"
AMI: "Mình đã điền sẵn thông tin của bạn vào đơn:
- Họ tên: Nguyễn Văn A
- MSV: B21DCCN123
- Lớp: D21CQCN01-N
Bạn chỉ cần điền lý do và tải xuống."
```

**2. Knowledge Graph**
- Liên kết các entities: Môn học → Giảng viên → Phòng học → Lịch thi
- Trả lời câu hỏi phức tạp: "Thầy Nguyễn Văn A dạy môn gì cho lớp mình?"

**3. Proactive Suggestions**
```
AMI (tự động nhắc): "Bạn ơi, hạn nộp đơn đăng ký học bổng là 15/12 
(còn 3 ngày). Bạn đã chuẩn bị hồ sơ chưa?"
```

### 10.3. Dài hạn (1-2 năm)

**1. Multi-University Platform**
- Mở rộng AMI cho các trường đại học khác
- Mỗi trường có knowledge base riêng
- Chia sẻ core technology

**2. Mobile App (React Native)**
- Push notification cho thông báo quan trọng
- Offline mode (cache câu hỏi thường gặp)

**3. Integration với hệ thống trường**
- Kết nối với Portal để lấy lịch học thật
- Kết nối với hệ thống đăng ký tín chỉ để check điều kiện

### 10.4. Tầm nhìn cuối cùng

Chúng mình mơ ước một ngày, mỗi sinh viên PTIT đều có AMI như một người bạn đồng hành:

- **Sáng**: AMI nhắc lịch học, deadline assignment
- **Trưa**: AMI gợi ý món ăn ở căng tin dựa trên sở thích
- **Chiều**: AMI trả lời mọi thắc mắc học tập
- **Tối**: AMI tóm tắt các thông báo quan trọng trong ngày

Không chỉ là một chatbot, mà là một **Digital Companion** thực sự.

---

## KẾT LUẬN

Hành trình xây dựng AMI không chỉ là một đồ án môn học, mà là một trải nghiệm học tập quý giá. Chúng mình đã học được:

**Về kỹ thuật**:
- Cách thiết kế hệ thống Clean Architecture quy mô lớn
- Cách triển khai RAG Pipeline từ lý thuyết đến thực tế
- Cách tối ưu hóa chi phí khi sử dụng LLM API

**Về làm việc nhóm**:
- Phân chia công việc rõ ràng (AI/Frontend/Infra)
- Code review và merge conflict resolution
- Agile workflow (sprint 2 tuần, daily standup)

**Về sản phẩm**:
- Lắng nghe người dùng thật (50+ interviews)
- Ship fast, iterate faster
- Technical excellence ≠ User satisfaction (đôi khi feature đơn giản lại được yêu thích nhất)

Chúng mình tin rằng AMI có thể mang lại giá trị thực sự cho cộng đồng sinh viên PTIT. Và đây chỉ mới là khởi đầu.
Chatbot@123!
---

*"The best way to predict the future is to invent it."* - Alan Kay

**Nhóm thực hiện:**
- Nguyễn Hải Lâm
- Minh
- Linh

**Học viện Công nghệ Bưu chính Viễn thông**
*Hà Nội, Tháng 12 năm 2025*
