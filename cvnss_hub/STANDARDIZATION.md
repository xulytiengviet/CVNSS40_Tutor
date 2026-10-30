# Đề xuất chuẩn hóa và phổ biến CVNSS4.0

Ngày: 30/10/2026. Đây là đề xuất phát triển, chưa phải đặc tả được tác giả phê duyệt.

## Căn cứ và giới hạn

Đã đọc tài liệu và source registry của CVNSS40_Tutor. Hai nguồn sơ cấp được đăng ký:
- https://chuvietnhanh.sourceforge.net/
- https://chuvietnhanh.sourceforge.net/TomGonCongThucCVNSS.htm

Registry hiện ghi `linked_not_ingested`: chưa đủ căn cứ nói đã đọc, lập chỉ mục hoặc chuẩn hóa toàn bộ nội dung hai website. MCP kết nối từ plugin không có trong phiên này; đã dùng Oracle cục bộ trong kho. Oracle vượt 23 ca tự kiểm tra; đây không phải tỷ lệ chính xác trên ngôn ngữ thực tế. Chuẩn nội bộ được đề xuất ở đây không có nghĩa là tiêu chuẩn quốc gia hoặc được mọi tổ chức công nhận.

## 1. Bộ hồ sơ tri thức

| Nhóm | Nội dung phải biên soạn | Bằng chứng cần có |
| --- | --- | --- |
| Khởi đầu, lịch sử | Tác giả, mục tiêu ban đầu, mốc thời gian, các phiên bản và khác biệt | Tài liệu gốc có ngày, trích đoạn, xác nhận tác giả khi cần |
| Khái niệm | Tên đầy đủ, định nghĩa CVNSS4.0, CQN, CVN, CVSS; thuật ngữ âm/chữ/mã | Từ điển thuật ngữ và dẫn nguồn cho từng định nghĩa |
| Bản chất | Phạm vi biểu diễn, quan hệ với chữ Quốc ngữ, giới hạn diễn giải | Đặc tả gốc; tách rõ mô tả của tác giả và phân tích kỹ thuật |
| Đặc điểm | Tập ký hiệu, Unicode, hoa/thường, dấu, cấu trúc âm tiết, bảo toàn định dạng | Quy tắc có điều kiện và ví dụ kiểm chứng |
| Chức năng | Viết, đọc, chuyển đổi, tra cứu, giải thích, luyện tập | Hợp đồng đầu vào/đầu ra và bài kiểm tra tương ứng |
| Quy tắc, công thức | Quy tắc theo từng chiều chuyển đổi, ưu tiên, ngoại lệ và xung đột | Mã quy tắc, nguồn, phiên bản, tập kiểm thử |
| Giá trị | Độ gọn, tốc độ học/đọc/gõ, khả năng tiếp cận | Thí nghiệm có đối chứng; công bố kết quả và giới hạn |
| Ứng dụng | Công cụ học, bàn phím, API, tài liệu song song, tích hợp phần mềm | Tình huống sử dụng, người dùng mục tiêu, tiêu chí nghiệm thu |
| Giới hạn | Mơ hồ khi giải mã, tên riêng, từ vay mượn, trường hợp chưa hỗ trợ | Danh sách lỗi, phản ví dụ, hướng xử lý rõ ràng |

## 2. Một mẫu dữ liệu thống nhất

Mỗi mục tri thức cần có: `id`, `type`, `title`, `definition`, `scope`, `source_url`, `source_version`, `source_locator`, `exact_quote`, `retrieved_at`, `content_sha256`, `license_status`, `evidence_status`, `reviewer`, `reviewed_at`, `related_rule_ids`, `examples`, `counterexamples`, `test_ids`, `introduced_in`, `supersedes`.

Không dùng một điểm tin cậy tự sinh để thay bằng chứng. Nhãn bằng chứng nên gồm: nguồn gốc, chính sách bộ chuyển đổi, quan sát thực nghiệm, đề xuất, chưa đủ bằng chứng. Tình trạng duyệt là trường riêng: nháp, đang đối chiếu, đã duyệt, bị thay thế, đang tranh luận. Chỉ dùng nguyên văn ngắn trong phạm vi quyền cho phép; ghi rõ giấy phép và quyền tái sử dụng.

## 3. Đặc tả quy tắc có thể kiểm thử

Mỗi quy tắc có `rule_id`, chiều chuyển đổi, mẫu vào, điều kiện áp dụng, phép biến đổi, thứ tự ưu tiên, ngoại lệ, mã quy tắc xung đột và nguồn. Gắn ví dụ với kết quả Oracle. Duy trì hai phiên bản độc lập: phiên bản tài liệu quy phạm và phiên bản thực thi. Khi khác nhau, ghi lỗi/khác biệt thay vì sửa âm thầm tài liệu hoặc thuật toán.

Giải mã cần trả cả chuỗi đầu vào, bản đọc được chọn, các ứng viên, quy tắc chọn mặc định và trạng thái mất thông tin. Ví dụ kiểm thử hiện có: `ed` có ứng viên `ề` và `oet`; bộ chuyển đổi chọn mặc định `ề`. Không khẳng định bản mặc định chính là ý định ban đầu của người viết.

## 4. Kho nguồn và trợ lý có dẫn chứng

Luồng đề xuất: danh mục nguồn → kiểm tra quyền thu thập → lưu phiên bản và checksum → tách đoạn theo mục → gắn quy tắc/khái niệm → người duyệt → lập chỉ mục phiên bản đã duyệt → truy hồi → trả lời kèm trích dẫn.

Ưu tiên nguồn gốc; phân biệt tài liệu tác giả, mã triển khai, nghiên cứu độc lập và đóng góp cộng đồng. Không tự coi website được liên kết là tài liệu đã nhập. Khi nguồn mâu thuẫn, nêu từng phiên bản và đoạn liên quan. LLM giải thích trên chứng cứ; chuyển đổi chính xác giao cho Oracle. Chưa có chứng cứ thì nói rõ phần chưa biết. Không nhập dữ liệu riêng tư vào dịch vụ MCP công khai.

## 5. Phục vụ nhiều người

- Người mới: bài nhập môn ngắn, giải thích thuật ngữ, hiển thị song song chữ gốc và mã, bài tập có đáp án đã kiểm chứng.
- Giáo viên: giáo án theo mục tiêu học tập, ngân hàng bài tập gắn quy tắc, tài liệu in và xuất dữ liệu theo quyền nguồn.
- Người dùng thường xuyên: chuyển đổi hai chiều, tô rõ đoạn mơ hồ, hoàn tác, giữ bản gốc và cảnh báo trường hợp chưa hỗ trợ.
- Lập trình viên: đặc tả API, JSON Schema, mã lỗi, phiên bản Oracle, bộ vector chuẩn và hướng dẫn tương thích.
- Người nghiên cứu: tập dữ liệu có giấy phép, tập đánh giá giữ riêng, lịch sử phiên bản và báo cáo lỗi tái lập.
- Khả năng tiếp cận: điều khiển bàn phím, độ tương phản, trình đọc màn hình và đọc bản chữ Quốc ngữ đi kèm. Khả năng đọc trực tiếp CVNSS bằng TTS cần đánh giá riêng.

## 6. Đo lường trước khi tuyên bố giá trị

Đánh giá chuyển đổi theo từng nhóm quy tắc; kiểm tra lỗi ký tự/từ, tỷ lệ mã mơ hồ, độ bao phủ và độ trễ. Đánh giá vòng khứ hồi riêng trên phần có thể đảo và phần mất thông tin. Đánh giá trợ lý theo độ đúng trích dẫn, nguồn có thực sự hỗ trợ phát biểu, xử lý thiếu nguồn và mâu thuẫn. Đánh giá người học theo độ hiểu, tốc độ đọc/gõ, tỷ lệ lỗi và khả năng ghi nhớ sau thời gian định trước.

So sánh độ dài phải nói rõ đếm byte, mã Unicode, cụm ký tự hay phím gõ. Không dùng số ca self-test để suy ra phần trăm chính xác; không khẳng định phổ cập hoặc thay thế chữ Quốc ngữ khi chưa có căn cứ.

## 7. Lộ trình đề xuất, chưa phải cam kết lịch

1. Nền tảng: kiểm kê nguồn, quyền sử dụng, thuật ngữ và lịch sử; chốt phạm vi CVNSS4.0 với tác giả/người duyệt được chỉ định.
2. Đặc tả: biên soạn quy tắc, ngoại lệ, mơ hồ, khác biệt phiên bản và vector kiểm thử; mỗi mục được duyệt có dẫn chứng.
3. Tri thức: nhập tập tài liệu được phép, lập chỉ mục có phiên bản, tạo bộ câu hỏi kiểm định độc lập; kiểm tra trích dẫn trước phát hành.
4. Phổ biến: thí điểm với người mới, giáo viên và lập trình viên; sửa theo bằng chứng rồi mở rộng.

Tiêu chí phát hành: mọi mục mang nhãn đã duyệt có nguồn và người duyệt; mọi quy tắc có kiểm thử phù hợp; mọi mơ hồ đã biết có cách hiển thị; không còn lỗi nghiêm trọng chưa xử lý trong phạm vi công bố. Những mục thiếu bằng chứng ở trạng thái mở, không điền bằng suy đoán.
