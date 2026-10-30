# Dùng CVNSS4.0 Knowledge Hub như plugin trong ChatGPT

## Hiện trạng
- Đây là mã nguồn **trên nhánh tính năng**, chưa merge / chưa triển khai.
- MCP hỗ trợ `stdio` (mặc định) và `streamable-http` (tùy chọn `--http`).
- Không có URL HTTPS đang vận hành; repo GitHub không phải là MCP endpoint.
- REST route `/api/cvnss4` là một giao diện khác, không thay cho `/mcp`.

## 1. Chạy thử trên Windows (môi trường Python + Node.js)
Từ PowerShell:

```powershell
git clone -b feature/cvnss4-knowledge-hub https://github.com/xulytiengviet/CVNSS40_Tutor.git
cd CVNSS40_Tutor
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install "mcp>=1.8,<2"
python -m cvnss_hub.mcp_server --http --host 127.0.0.1 --port 8000
```

MCP local endpoint: `http://127.0.0.1:8000/mcp`.
Cần kiểm tra phiên bản Python MCP SDK tương thích khi triển khai thực tế.

## 2. Kiểm tra MCP trước khi kết nối
Chạy một cửa sổ terminal khác:

```powershell
npx @modelcontextprotocol/inspector@latest
```

Chọn **Streamable HTTP**, nhập `http://127.0.0.1:8000/mcp`, kết nối, liệt kê và thử các tool:
- `cvnss_convert`
- `cvnss_inspect`
- `cvnss_candidates`
- `cvnss_audit`
- `cvnss_self_test`

Trước khi cho ChatGPT truy cập qua mạng, phải triển khai lên một host HTTPS được bảo vệ hoặc cấu hình **Secure MCP Tunnel** và kiểm tra allowlist Host/Origin của SDK. Không dùng URL localhost trực tiếp trong ô kết nối ChatGPT trên web, không bỏ qua authentication để mở một máy chủ công khai.

## 3. Tạo plugin trong ChatGPT
Theo tài liệu chính thức (2026):
1. Mở **Plugins** trong ChatGPT.
2. Chọn **+ → Add custom MCP server**.
3. Đặt tên `CVNSS4.0 Knowledge Hub`.
4. Dưới **Connection**, nhập URL MCP HTTPS đã triển khai, dạng `https://<your-host>/mcp`, hoặc chọn **Tunnel** nếu có.
5. Cấu hình xác thực và xem xét cảnh báo bảo mật.
6. Chọn **Create as a plugin**; xác nhận server tìm thấy 5 công cụ rồi cài plugin.
7. Trong chat, chọn **@CVNSS4.0 Knowledge Hub** trước câu hỏi.

Tài liệu tham khảo:
- https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- https://developers.openai.com/plugins/deploy/connect-chatgpt

## 4. Ví dụ sử dụng
**Câu hỏi chuyển đổi**: “@CVNSS4.0 Knowledge Hub Hãy chuyển ‘Tiếng Việt’ từ CQN sang CVSS; giữ nguyên chữ hoa.”

**Kết quả Oracle v5.0:** `Tiếng Việt` → `Tizb Vidf`.

**Giải mã nhập nhằng**: “Kiểm tra mã `ed`, liệt kê mọi ứng viên trước khi kết luận.”
Oracle trả `["ề", "oet"]`; mặc định `selected: "ề"`. Vì có nhập nhằng nên không thể bảo đảm mọi câu được giải mã nguyên văn tuyệt đối.

**Giảng dạy**: “Dựa vào tài liệu công thức chính thức, giải thích 5 nhóm quy tắc và ra 10 bài tập.”
Phần giảng dạy **đòi hỏi Knowledge Base/RAG đã nhập liệu**. MCP hiện tại chỉ có Oracle chuyển đổi và kiểm toán; không tự cung cấp toàn bộ tài liệu nguồn.

## 5. Ranh giới và bảo mật
- Công khai MCP liên quan đến input văn bản người dùng: yêu cầu HTTPS, xác thực hoặc giới hạn tin cậy, kiểm soát tốc độ và theo dõi sử dụng.
- Không lưu trữ key trong repo. Không tải nguồn mà không xét quyền sử dụng/robots.
- Không tuyên bố có độ chính xác 99,8% hoặc tri thức bao phủ 100% nếu chưa benchmark và chưa hoàn tất crawling/RAG.
- Tách dữ liệu nguồn gốc và giải thích AI; dùng bộ chuyển đổi đã kiểm thử như nguồn đáp án xác định.
