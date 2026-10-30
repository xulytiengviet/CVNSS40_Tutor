# Kết nối CVNSS4.0 Knowledge Hub với ChatGPT Plugin/MCP (Windows)

> Tình trạng: mã nguồn có MCP server `stdio` và `Streamable HTTP`, REST API xác thực qua DeepTutor, nhưng **chưa có HTTPS MCP URL được triển khai** và **chưa kết nối với bất kỳ tài khoản ChatGPT nào**. Hướng dẫn này phân biệt rõ chế độ thử nghiệm cục bộ với kết nối sản phẩm thực tế.

## 1. Thành phần và giới hạn

| Thành phần | Chức năng | Trạng thái |
|---|---|---|
| Converter v5.0.0-audit-safe | CQN ↔ CVN ↔ CVSS; xử lý nhập nhằng minh bạch | Đã có mã nguồn, kiểm thử oracle 23/23 |
| MCP (`cvnss_hub/mcp_server.py`) | 6 read-only tools: convert, inspect, candidates, audit, self_test, sources | Cần chạy server |
| DeepTutor REST (`/api/cvnss4/*`) | 7 endpoint; áp dụng chính sách `authenticated` của máy chủ DeepTutor | Có route qua manifest, cần khởi động DeepTutor |
| Knowledge registry (`sources.json`) | Danh mục URL, loại nguồn và trạng thái nhập dữ liệu | Danh mục ban đầu; **chưa crawl toàn bộ** |
| RAG, L1/L2/L3, Quiz, Task Board | Chức năng đang có của DeepTutor | Chưa nối trực tiếp vào 6 công cụ MCP này |

**Không đồng nhất REST API và MCP**: `/api/cvnss4/convert` không phải một MCP server. ChatGPT cần `https://ten-mien-thuc-te/mcp` hoặc Secure MCP Tunnel. `http://127.0.0.1:8000/mcp` chỉ dùng trong máy để thử nghiệm.

## 2. Chuẩn bị môi trường Windows

Yêu cầu: Windows PowerShell, Git, Node.js (khuyến nghị 22 LTS), Python 3.11–3.14; đã có tài khoản/không gian làm việc ChatGPT đủ quyền kết nối custom MCP.

### Lấy mã nguồn

```powershell
git clone https://github.com/xulytiengviet/CVNSS40_Tutor.git
cd CVNSS40_Tutor
```

Nếu PR #1 chưa hợp nhất vào `main`, chuyển sang nhánh:
```powershell
git fetch origin
git switch feature/cvnss4-knowledge-hub
```

### Cài môi trường tối thiểu cho CVNSS4.0 MCP

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install "mcp>=1.26.0,<2.0.0" pytest
node --version
```

Không cần cài toàn bộ DeepTutor nếu chỉ muốn chạy MCP Oracle. Dùng trực tiếp `\.venv\Scripts\python.exe` để tránh lỗi PowerShell ExecutionPolicy khi kích hoạt môi trường ảo.

### Kiểm tra converter

```powershell
.\.venv\Scripts\python.exe -c "from cvnss_hub.service import execute; print(execute('self_test'))"
.\.venv\Scripts\python.exe -c "from cvnss_hub.service import execute; print(execute('convert', text='Tiếng Việt', mode='cqn'))"
.\.venv\Scripts\python.exe -m pytest tests/test_cvnss_hub.py -q
```

Kỳ vọng: `self_test.ok=true`, `tests=23`, `failures=[]`; `Tiếng Việt` cho `cvss='Tizb Vidf'`. Đây là **bộ tự kiểm thử nội bộ**, không phải chứng minh mọi câu đều giải mã lossless.

## 3. Chạy MCP

### A. Chạy trực tiếp qua stdio (Codex, Claude Desktop, các khách MCP cục bộ)

```powershell
.\.venv\Scripts\python.exe -m cvnss_hub.mcp_server
```

Cấu hình cho khách MCP cục bộ (đường dẫn phải thay bằng đường dẫn thật của máy):

```json
{
  "mcpServers": {
    "cvnss4": {
      "command": "C:\\duong-dan\\CVNSS40_Tutor\\.venv\\Scripts\\python.exe",
      "args": ["-m", "cvnss_hub.mcp_server"],
      "cwd": "C:\\duong-dan\\CVNSS40_Tutor"
    }
  }
}
```

`stdio` **không** có URL, không phải kết nối từ ChatGPT web.

### B. Chạy Streamable HTTP cục bộ

```powershell
.\.venv\Scripts\python.exe -m cvnss_hub.mcp_server --http --host 127.0.0.1 --port 8000
```

Mở thêm cửa sổ PowerShell:

```powershell
npx --yes @modelcontextprotocol/inspector@latest
```

Trong Inspector: chọn **Streamable HTTP**, nhập `http://127.0.0.1:8000/mcp`, Connect → List Tools → gọi `cvnss_self_test`, `cvnss_convert`, `cvnss_inspect` và `cvnss_sources`.

Chú ý server hiện chỉ cho bind loopback (`127.0.0.1`/`localhost`/`::1`) để tránh vô tình mở một MCP **không xác thực** ra Internet. Không tắt rào chắn này chỉ để tránh lỗi kết nối.

## 4. Đưa MCP lên HTTPS / Secure MCP Tunnel

ChatGPT trên web **không kết nối trực tiếp localhost**. Hai phương án được OpenAI hỗ trợ:

- **Secure MCP Tunnel** (ưu tiên nếu máy chủ nằm trong máy cá nhân/mạng riêng): tạo tunnel theo hướng dẫn dành cho tài khoản/workspace của bạn, chọn server `stdio` hoặc HTTP `127.0.0.1:8000`, rồi chọn `Tunnel` trong ChatGPT. Tunnel có thể cần chính sách workspace và công cụ client tương ứng.
- **HTTPS MCP Endpoint**: đặt một reverse proxy có TLS, xác thực và giới hạn truy cập phía trước MCP. Giữ backend bind `127.0.0.1`. Chỉ cung cấp URL thực sau khi có máy chủ và kiểm tra thành công. Không tạo URL `*.pages.dev` hoặc URL GitHub Pages giả làm MCP.

Khi dùng reverse proxy, kiểm tra `Host`/`Origin` allowlist của Python MCP SDK; thông báo `421 Invalid Host` hoặc `403 Invalid Origin` nghĩa là cấu hình an ninh chưa khớp. Không tắt DNS rebinding protection trên máy chủ mở công khai. Dùng HTTPS, ủy quyền người gọi, rate limit, giới hạn nội dung và nhật ký phù hợp. HTTP MCP demo không tự tích hợp OAuth.

Tài liệu:
- https://developers.openai.com/plugins/deploy/connect-chatgpt
- https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt
- https://github.com/modelcontextprotocol/python-sdk/blob/main/docs/run/deploy.md

## 5. Thêm vào ChatGPT

Quyền tạo custom MCP phụ thuộc gói thuê bao và chính sách workspace; **sự tồn tại của mã nguồn không bảo đảm mọi tài khoản có nút này**.

1. Trên ChatGPT web, vào **Plugins**, chọn **+ → Add custom MCP server**.
2. Đặt tên `CVNSS4.0 Knowledge Hub`, mô tả `Chuyển đổi/kiểm toán CVNSS4.0 và truy xuất danh mục nguồn gốc`.
3. Trong **Connection**, nhập endpoint HTTPS MCP thật (kết thúc `/mcp`) **hoặc** chọn Secure MCP Tunnel đã cấu hình.
4. Thiết lập xác thực của server, đọc cảnh báo rủi ro, xác nhận.
5. Chọn **Create as a plugin**.
6. Kiểm tra ChatGPT đã phát hiện đúng 6 công cụ; cài plugin, mở chat mới, gõ `@` chọn plugin rồi đặt câu hỏi.
7. Khi cập nhật danh mục công cụ, vào cấu hình plugin và **Refresh** để ChatGPT nạp lại schema.

Ví dụ câu hỏi sau khi kết nối:

- `@CVNSS4.0 Knowledge Hub Gọi cvnss_convert để chuyển "Tiếng Việt" từ cqn sang cvss, đừng tự suy đoán.`
- `@CVNSS4.0 Knowledge Hub Gọi cvnss_inspect cho "ed" và nêu mọi candidates cùng lựa chọn canonical.`
- `@CVNSS4.0 Knowledge Hub Gọi cvnss_sources và cho biết tài liệu nào là nguồn gốc, tài liệu nào chưa nhập RAG.`
- `@CVNSS4.0 Knowledge Hub Hãy chạy cvnss_self_test; cho biết số ca và lỗi (nếu có).`

Các chức năng giảng dạy như `Hãy ra 20 câu hỏi từ toàn bộ tư liệu nguồn` **chưa** được 6 công cụ này cung cấp: cần kết nối tiếp DeepTutor Knowledge Base đã nạp dữ liệu và workflow quiz / mastery.

## 6. Công cụ hiện có

| Công cụ MCP | Tham số chính | Trả về |
|---|---|---|
| `cvnss_convert` | `text`, `mode=cqn|cvn|cvss` | `cqn, cvn, cvss` |
| `cvnss_inspect` | `word`, `source=cvss|cvn` | phân đoạn, danh sách ứng viên, canonical, critical |
| `cvnss_candidates` | `word`, `source` | mọi ứng viên |
| `cvnss_audit` | không | thông số audit |
| `cvnss_self_test` | không | `ok, tests, failures` |
| `cvnss_sources` | không | seed registry có URL và trạng thái |

Bộ CVNSS4.0 v5.0-audit-safe sử dụng bảng chuẩn, patch và quy tắc canonical minh bạch. Ví dụ mã `ed` có các ứng viên `ề` và `oet`, chọn `ề` theo chính sách canonical: vì thế không hứa giải mã khôi phục nguyên văn với mọi chuỗi đầu vào.

## 7. REST API tích hợp DeepTutor (không phải MCP)

Khi chạy ứng dụng DeepTutor server (có cài module server) theo hướng dẫn gốc và xác thực người dùng, FastAPI có route `/api/cvnss4/health`, `/convert`, `/inspect`, `/candidates`, `/sources`, `/audit`, `/self-test` từ core manifest với chính sách **authenticated**. Kiểm tra OpenAPI schema trên máy chủ sau khi khởi động. REST endpoint không được dùng thay `/mcp` trong ô tùy chỉnh MCP ChatGPT.

## 8. Chẩn đoán

| Dấu hiệu | Nguyên nhân và xử lý |
|---|---|
| `python: No module named mcp` | Cài đúng venv: `\.venv\Scripts\python.exe -m pip install "mcp>=1.26.0,<2.0.0"` |
| `node not found` | Cài Node.js, mở lại PowerShell, kiểm tra `node --version` |
| `Connection refused` | Terminal MCP chưa chạy; kiểm tra 127.0.0.1:8000; tránh trùng port |
| `404 /mcp` | Dùng đúng Streamable HTTP mode và đúng path, không dùng REST path |
| `421 Invalid Host` hoặc `403 Invalid Origin` | Rà soát reverse proxy, Host/Origin và cấu hình chống DNS rebinding |
| Không thấy plugin trong ChatGPT | Xem quyền gói/workspace; chỉ ChatGPT web; kiểm tra connection và cài đặt plugin |
| Công cụ cũ sau khi deploy | Refresh tool metadata trong plugin và mở chat mới |
| Kết quả giải mã khác văn bản ban đầu | Kiểm tra `cvnss_inspect`; quy tắc many-to-one có nhập nhằng |

## 9. Bảo mật, quyền sử dụng và độ chính xác

Không lưu API key, token, nội dung cá nhân hoặc memory dùng chung trong `sources.json` hay GitHub. Nguồn chính thức phải được ghi nguồn tác giả, phiên bản, quyền sử dụng trước khi ingest. Tài liệu/tệp web chỉ là **dữ liệu**, không được phép trở thành lệnh cho tác nhân AI.

Hướng mở rộng tiếp theo: crawl có kiểm soát, làm sạch quy tắc/tài liệu, versioned RAG, giáo trình, kiểm thử/quiz, đồ thị memory L1–L3, benchmark khách quan và bộ plugin có UI. Không quảng cáo những phần này đã hoàn thành.
