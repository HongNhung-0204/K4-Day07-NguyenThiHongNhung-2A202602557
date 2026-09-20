# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Uống nước đẹp da
**Thành viên:** Nguyễn Thị Hồng Nhung, Nguyễn Bảo Sơn, Vũ Văn Điền
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách trả hàng và hoàn tiền trên Shopee.

**Tại sao nhóm chọn chủ đề này?**

Nhóm chọn chủ đề này vì tài liệu có nhiều quy định cụ thể về thời hạn, điều kiện, bằng chứng và phương thức hoàn tiền. Đây là bộ dữ liệu phù hợp để kiểm tra retrieval theo câu hỏi thực tế và so sánh ảnh hưởng của chunking.

### Danh sách tài liệu (Data Inventory)

Corpus gồm **10 tài liệu**, lấy ngày 20/09/2026, tổng cộng khoảng **59.744 ký tự**. Dữ liệu nằm trong `data/shopee-return-refund/`; nguồn được ghi trong `sources.csv`.

| #   | Tài liệu                       | Category             | Số ký tự | Audience |
| --- | ------------------------------ | -------------------- | -------: | -------- |
| 1   | general-return-refund-rules    | returns-policy       |    6.270 | buyer    |
| 2   | refund-timing-and-methods      | refund-process       |   11.094 | buyer    |
| 3   | restricted-return-products     | product-restrictions |    1.295 | buyer    |
| 4   | return-by-change-of-mind       | returns-policy       |    7.209 | buyer    |
| 5   | return-refund-evidence         | evidence             |    3.277 | buyer    |
| 6   | return-shipping-packaging-fees | return-shipping      |   15.753 | buyer    |
| 7   | review-return-request          | review-process       |    8.161 | buyer    |
| 8   | seller-refund-dispute          | seller-process       |    1.137 | buyer    |
| 9   | submit-return-refund-request   | request-process      |    4.281 | buyer    |
| 10  | track-return-request           | request-status       |    1.267 | buyer    |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Corpus chỉ chứa nội dung chính sách công khai, không có dữ liệu cá nhân hoặc thông tin đăng nhập.
- [x] Mỗi tài liệu đã có URL nguồn trong front matter và `sources.csv`.

### Cấu trúc Metadata (Metadata Schema)

| Trường        | Kiểu    | Ví dụ                         | Tác dụng                  |
| ------------- | ------- | ----------------------------- | ------------------------- |
| `doc_id`      | string  | `general-return-refund-rules` | Nhận diện và xóa tài liệu |
| `source_url`  | string  | URL Shopee                    | Truy nguyên nguồn         |
| `audience`    | string  | `buyer`                       | Lọc theo đối tượng        |
| `category`    | string  | `returns-policy`              | Lọc theo loại chính sách  |
| `chunk_index` | integer | `1`                           | Xác định vị trí chunk     |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu                    | Chiến lược | Số chunk | Độ dài trung bình | Nhận xét                        |
| --------------------------- | ---------- | -------: | ----------------: | ------------------------------- |
| general-return-refund-rules | FixedSize  |       14 |             494.5 | Dễ triển khai, đôi khi cắt bảng |
| general-return-refund-rules | Sentence   |        9 |             695.1 | Giữ câu nhưng chunk dài         |
| general-return-refund-rules | Recursive  |       17 |             367.3 | Giữ ranh giới nội dung tốt hơn  |

### Chiến lược của từng thành viên

**Nguyễn Thị Hồng Nhung**

- **Loại chiến lược:** FixedSizeChunker + OpenAI `text-embedding-3-small`
- **Mô tả:** Chunk 500 ký tự, overlap 50; phù hợp làm baseline và đạt 4/5 câu liên quan trong top-3.

**Nguyễn Bảo Sơn**

- **Loại chiến lược:** Baseline in-memory + MockEmbedder
- **Mô tả:** Ưu tiên pipeline đơn giản, chạy nhanh và không cần API key; báo cáo cá nhân ghi nhận 5/5 câu liên quan.

**Vũ Văn Diễn**

- **Loại chiến lược:** HeadingChunker + MockEmbedder + metadata filter
- **Mô tả:** Chia theo tiêu đề để giữ chủ đề chính; thử lọc `buyer`/`seller`, đạt 1/5 theo báo cáo cá nhân.

| Thành viên            | Chiến lược              |          Kết quả | Điểm mạnh               | Điểm yếu                      |
| --------------------- | ----------------------- | ---------------: | ----------------------- | ----------------------------- |
| Nguyễn Thị Hồng Nhung | FixedSize + OpenAI      |              4/5 | Embedding có ngữ nghĩa  | Có thể cắt điều khoản         |
| Nguyễn Bảo Sơn        | Baseline + Mock         | 5/5 theo báo cáo | Nhanh, đơn giản         | Điểm không phản ánh ngữ nghĩa |
| Vũ Văn Diễn           | Heading + Mock + filter | 1/5 theo báo cáo | Giữ cấu trúc, có filter | Phụ thuộc mock embedding      |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

Với corpus tiếng Việt, nhóm đánh giá kết hợp heading/recursive chunking với embedding thực tế là hướng phù hợp nhất. FixedSize + OpenAI là baseline tốt để so sánh; heading giúp giữ trọn ngữ nghĩa điều khoản.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| #   | Câu hỏi                                                 | Gold answer                                                   | Chunk liên quan                 |
| --- | ------------------------------------------------------- | ------------------------------------------------------------- | ------------------------------- |
| 1   | Thời hạn gửi yêu cầu với thực phẩm tươi sống?           | Trong vòng 24 giờ từ khi cập nhật giao hàng thành công.       | `general-return-refund-rules#1` |
| 2   | Đơn người bán tự vận chuyển có thời hạn bao nhiêu ngày? | 15 ngày sau khi bấm đã nhận hàng hoặc 20 ngày nếu chưa bấm.   | `general-return-refund-rules#1` |
| 3   | Mở hộp kiểm tra có được trả hàng do đổi ý không?        | Thông thường không nếu mở hộp làm mất tính nguyên vẹn.        | `return-by-change-of-mind#13`   |
| 4   | Cần bằng chứng gì khi nhận hàng bị lỗi?                 | Video mở kiện liên tục, rõ mã vận đơn và tình trạng sản phẩm. | `return-refund-evidence#1`      |
| 5   | Hoàn tiền qua ShopeePay mất bao lâu?                    | Khoảng 24 giờ sau khi yêu cầu được chấp nhận.                 | `refund-timing-and-methods#8`   |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| #   | Câu hỏi                 | Chiến lược tốt nhất | Chunk liên quan top-3? | Ghi chú                     |
| --- | ----------------------- | ------------------- | ---------------------- | --------------------------- |
| 1   | Thực phẩm tươi sống     | FixedSize + OpenAI  | Có                     | Top-1 score 0.5159          |
| 2   | Người bán tự vận chuyển | Heading/metadata    | Chưa                   | Cần tách riêng mục thời hạn |
| 3   | Mở hộp do đổi ý         | Heading + OpenAI    | Có                     | Top-1 score 0.7014          |
| 4   | Bằng chứng hàng lỗi     | FixedSize + OpenAI  | Có                     | Top-1 score 0.6700          |
| 5   | Hoàn tiền ShopeePay     | FixedSize + OpenAI  | Có                     | Top-1 score 0.6888          |

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích chính:**

- Embedding thực tế cải thiện rõ similarity và retrieval so với MockEmbedder.
- Chunk theo heading giữ điều khoản hoàn chỉnh; FixedSize đơn giản nhưng có thể cắt nội dung.
- Metadata phải phản ánh đúng dữ liệu, không gán `seller` cho tài liệu chỉ dành cho người mua.

**Bài học rút ra:**

Cùng một corpus nhưng embedding và cách chunking khác nhau tạo ra kết quả retrieval khác nhau. MockEmbedder phù hợp kiểm thử cấu trúc, còn OpenAI phù hợp đánh giá ngữ nghĩa tiếng Việt.

**Nếu làm lại:**

Thêm tài liệu `seller`, tách các mục thời hạn theo heading và chạy lại benchmark bằng cùng một embedding model cho cả ba thành viên.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí             |        Điểm |
| -------------------- | ----------: |
| Lựa chọn tài liệu    |     10 / 10 |
| Thiết kế chiến lược  |     13 / 15 |
| Chất lượng retrieval |      8 / 10 |
| Thuyết trình         |       5 / 5 |
| **Tổng phần nhóm**   | **36 / 40** |
