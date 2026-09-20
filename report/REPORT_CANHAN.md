# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thị Hồng Nhung
**Nhóm:** Uống nước đẹp da
**Ngày:** 20/9/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Hai vector có hướng gần nhau, nghĩa là hai văn bản có nội dung hoặc ngữ nghĩa tương tự. Giá trị càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**

- Câu A: Người mua có 15 ngày để gửi yêu cầu trả hàng.
- Câu B: Thời hạn yêu cầu trả hàng của người mua là 15 ngày.
- Tại sao tương đồng: Hai câu diễn đạt cùng một thông tin dù thứ tự từ khác nhau.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Sản phẩm bị lỗi và không hoạt động.
- Câu B: Hôm nay trời có mưa lớn.
- Tại sao khác: Hai câu thuộc hai chủ đề không liên quan.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**

Cosine tập trung vào hướng của vector nên phù hợp để so sánh ngữ nghĩa, ít bị ảnh hưởng bởi độ dài văn bản. Với embedding đã chuẩn hóa, tích vô hướng cũng chính là cosine similarity.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

`ceil((10,000 - 50) / (500 - 50)) = ceil(22.11) = 23` chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**

Khi overlap tăng lên 100, số chunk là `ceil((10,000 - 100) / (500 - 100)) = 25`. Overlap lớn giúp giữ ngữ cảnh ở ranh giới chunk tốt hơn, nhưng làm tăng số chunk và chi phí embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:

Tôi dùng regex `(?<=[.!?])(?: +|(?<=\.)\r?\n)` để tách sau dấu câu và giữ lại dấu câu. Text rỗng trả về `[]`, khoảng trắng thừa được loại bỏ và số câu được gom theo `max_sentences_per_chunk`. Regex vẫn có thể tách chưa chính xác ở chữ viết tắt hoặc số thập phân.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:

Thuật toán ưu tiên các separator từ đoạn văn, dòng, câu, khoảng trắng đến ký tự. Các mảnh nhỏ liền nhau được gom lại không vượt `chunk_size`; mảnh quá dài được xử lý đệ quy với separator thấp hơn. Base case là text rỗng, text đã đủ ngắn hoặc không còn separator thì cắt trực tiếp theo kích thước.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:

Mỗi `Document` được sao chép metadata, tạo embedding và lưu trong danh sách in-memory. Khi search, query được embedding rồi tính tích vô hướng với các vector tài liệu; kết quả được sắp xếp giảm dần theo score.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:

`search_with_filter` lọc metadata trước khi tính similarity để loại bỏ ứng viên không phù hợp. `delete_document` xóa tất cả record có `metadata["doc_id"]` trùng với ID được yêu cầu và trả về trạng thái thành công/thất bại.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:

Agent truy xuất top-k chunk, ghép chúng thành phần `Context`, sau đó đặt context và câu hỏi vào một prompt. Prompt yêu cầu mô hình chỉ trả lời dựa trên context; kết quả cuối cùng được trả về từ `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
42 passed in 0.09s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A                                        | Câu B                                             | Dự đoán | Điểm thực tế | Đúng? |
| --- | -------------------------------------------- | ------------------------------------------------- | ------- | ------------ | ----- |
| 1   | Thời hạn trả hàng là 15 ngày.                | Người mua có 15 ngày để gửi yêu cầu trả hàng.     | cao     | 0.8930       | Có    |
| 2   | Shopee hoàn tiền qua ShopeePay trong 24 giờ. | Tiền hoàn được gửi vào ví ShopeePay sau một ngày. | cao     | 0.7512       | Có    |
| 3   | Sản phẩm bị lỗi và không hoạt động.          | Hôm nay trời có mưa lớn.                          | thấp    | 0.3143       | Có    |
| 4   | Người mua cần quay video mở kiện hàng.       | Sản phẩm cần được đóng gói bằng hộp carton.       | thấp    | 0.4598       | Có    |
| 5   | Hoàn tiền khi nhận hàng.                     | Người bán đăng sản phẩm mới lên cửa hàng.         | thấp    | 0.4836       | Có    |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Các điểm được tính bằng OpenAI `text-embedding-3-small` với vector 1536 chiều. Hai cặp đồng nghĩa có điểm cao, trong khi các cặp khác chủ đề có điểm thấp hơn; tuy nhiên điểm số vẫn cần được đánh giá cùng kết quả retrieval.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| #   | Câu hỏi (Query)                                         | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt)                                      |
| --- | ------------------------------------------------------- | ------------------------------------ | ---------- | ------------------------------ | -------------------------------------------------------------------- |
| 1   | Thời hạn gửi yêu cầu với thực phẩm tươi sống?           | `general-return-refund-rules#1`      | 0.5159     | Có trong top-3                 | Gold answer là 24 giờ.                                               |
| 2   | Đơn người bán tự vận chuyển có thời hạn bao nhiêu ngày? | `return-shipping-packaging-fees#13`  | 0.5527     | Không trong top-3              | Gold answer là 15 ngày hoặc 20 ngày tùy trạng thái đơn.              |
| 3   | Mở hộp kiểm tra có được trả hàng do đổi ý không?        | `return-by-change-of-mind#13`        | 0.7014     | Có trong top-3                 | Không được hỗ trợ nếu mở hộp làm mất tính nguyên vẹn.                |
| 4   | Cần bằng chứng gì khi nhận hàng bị lỗi?                 | `submit-return-refund-request#1`     | 0.6700     | Có trong top-3                 | Nên chuẩn bị video mở kiện hàng liên tục và rõ tình trạng sản phẩm.  |
| 5   | Hoàn tiền qua ShopeePay mất bao lâu?                    | `submit-return-refund-request#8`     | 0.6888     | Có trong top-3                 | ShopeePay thường nhận tiền trong 24 giờ sau khi chấp nhận hoàn tiền. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**

Tôi học được rằng embedding thực tế cải thiện rõ khả năng tìm đúng nội dung tiếng Việt. Tuy vậy, chunking và metadata vẫn quan trọng: câu hỏi về thời hạn người bán tự vận chuyển chưa tìm được chunk đúng trong top-3, cho thấy cần tinh chỉnh chiến lược chia chunk hoặc metadata.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí                                        | Điểm tự đánh giá |
| ----------------------------------------------- | ---------------- |
| Khởi động (Warm-up)                             | 5 / 5            |
| Hướng tiếp cận của tôi (My Approach)            | 10 / 10          |
| Hoàn thiện code (Core Implementation — tests)   | 30 / 30          |
| Dự đoán độ tương tự (Similarity Predictions)    | 3 / 5            |
| Kết quả truy xuất của tôi (Competition Results) | 6 / 10           |
| **Tổng phần cá nhân**                           | **54 / 60**      |
