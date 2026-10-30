# GitHub → CVNSS4.0 MCP → ChatGPT Plugin (đồng bộ có kiểm soát)

## Mục đích

Kết nối một lần và sử dụng plugin trong nhiều cuộc trò chuyện, tương tự trải nghiệm gọi GitHub plugin. Tuy nhiên, **đây là hai thứ khác nhau**:

- **Code sync:** GitHub tự triển khai mã server mới lên một host MCP đã liên kết. Điều này có thể tự động qua dịch vụ deploy GitHub (Render, Railway, Fly.io, VPS CI/CD). ChatGPT dùng cùng một URL MCP ổn định.
- **Tool metadata sync:** Khi thêm/đổi tên/sửa schema tool, trong ChatGPT cần **Refresh** danh sách tool theo chính sách của plugin/workspace. Không mặc nhiên tự cập nhật mọi schema hoặc thay đổi quyền.
- **Knowledge sync:** Thêm tài liệu vào GitHub không tự tạo RAG. Phải chạy ingestion + build/publish index có version trong DeepTutor; truy vấn MCP cần công cụ RAG (chưa có trong v0.1).
- **User memory sync:** Bộ nhớ L1–L3 đang thuộc phiên DeepTutor. Không tự lấy bộ nhớ cá nhân ChatGPT hay ghi đè tiến độ học tập nếu không có API, quyền và cơ chế phân vùng dữ liệu được thiết kế rõ.
- **Account sync:** GitHub Connector được OpenAI cung cấp sẵn và có flow kết nối riêng. MCP tự phát triển không thừa hưởng tự động OAuth, phân quyền, hoặc đồng bộ tài khoản GitHub/ChatGPT.

## Mô hình hoạt động

```text
GitHub xulytiengviet/CVNSS40_Tutor
  ├── cvnss_hub/                     # deterministic Oracle + MCP server
  ├── integrations/chatgpt-plugin/   # portable plugin.json + SKILL.md
  └── scripts/build_cvnss_chatgpt_plugin.py
          |
          | (A) CI/CD on main -> deploy MCP server to HTTPS host
          v
https://<your-real-domain>/mcp  [stable, authenticated]
          |
          | (B) Connect once: ChatGPT Plugins > + > Add custom MCP
          v
ChatGPT's CVNSS4.0 Knowledge Hub plugin (discover tools)
          |
          | (C) user explicitly invokes @CVNSS4.0 in chat
          v
MCP tool call -> converter/knowledge -> structured response
```

Phần (A) cần bạn kết nối một host do mình quản lý và bật triển khai tự động. Repo và ZIP plugin **không** tự mua/tạo server, domain, OAuth hoặc kết nối với tài khoản ChatGPT.

## Hướng triển khai sẵn trong repository

Đã có [Render Blueprint](../../render.yaml), [MCP Dockerfile](../../deploy/cvnss-mcp/Dockerfile) và [hướng dẫn triển khai từng bước](../../deploy/cvnss-mcp/README.md). Blueprint kết nối với GitHub trên nhánh `main`, tự triển khai khi CI xanh. Bản hosted ở giai đoạn này chỉ có 7 công cụ công khai, không đăng nhập, không có bộ nhớ cá nhân; trong ChatGPT chọn **No authentication**. OAuth 2.1 là hạng mục riêng nếu mở rộng ghi dữ liệu hoặc cá nhân hóa.

## 1. Hai loại gói plugin

### 1A. Gói Skills-only hiện có (không cần URL)

Chạy tại thư mục root:

```powershell
py scripts/build_cvnss_chatgpt_plugin.py
```

Kết quả: `dist/cvnss4-knowledge-hub-0.2.0.zip`, gồm `plugin.json` và `skills/cvnss4-tutor/SKILL.md`. Đây là hướng dẫn nghiệp vụ CVNSS4.0 cho AI, **không có công cụ chuyển đổi trực tuyến**, không có GitHub sync. File ZIP được tạo lại bằng GitHub Actions và đính kèm ở mục Artifacts của run CI `CVNSS4.0 Hub smoke tests`.

### 1B. Gói Skills + MCP remote (cần URL thật trước)

Khi **MCP endpoint HTTPS đã chạy và đã kiểm tra bằng MCP Inspector**:

```powershell
py scripts/build_cvnss_chatgpt_plugin.py --mcp-url https://ten-mien-thuc-te-cua-ban/mcp
```

Cùng file ZIP, nhưng có thêm `mcp.json` dưới root plugin trỏ vào endpoint này, với chuẩn `streamable-http`. Lệnh kiểm tra URL hợp lệ về cú pháp, **không** xác minh host có thật, xác thực hay hoạt động.

Không đưa URL thử nghiệm, token hay tài khoản mật vào ZIP. Khi dùng Plugin Creator để lưu plugin riêng, việc upload ZIP là một bước **tách biệt**, không đồng nghĩa server đã triển khai hoặc người dùng đã kết nối.

## 2. Đường đi triển khai thật: nối GitHub với một MCP host ổn định

**Khuyến nghị:** GitHub → PaaS/VM có HTTPS + OAuth/gateway xác thực → ChatGPT Plugin.

- Tạo web service/container *riêng* cho `cvnss_hub` (Python MCP SDK + Node.js converter) thay vì triển khai toàn bộ DeepTutor nặng.
- Liên kết GitHub repo và nhánh `main` với host. Bật `Auto Deploy: After CI Checks Pass` (nếu host hỗ trợ).
- Docker image phải có Node.js và Python, cài `mcp>=1.26.0,<2`. Chạy MCP `--http` dưới **private loopback** sau reverse proxy có TLS/xác thực, hoặc dùng **Secure MCP Tunnel** trên cùng mạng tin cậy.
- URL công khai dạng `https://<your-domain>/mcp` phải là endpoint của MCP thật, không phải GitHub Pages, REST `/api/cvnss4` hay `localhost`.
- Chỉ bật chế độ tự deploy **sau** khi CI và kiểm thử kết nối thành công. Có health-check, rollback, rate-limit và giám sát phù hợp.
- Không dùng GitHub Actions secret để cài plugin tự động vào tài khoản người dùng; kết nối và cấp quyền plugin do chính người dùng/workspace thực hiện.

Nếu chọn Render, tích hợp GitHub có thể tự tái triển khai khi commit vào nhánh liên kết và có chế độ đợi kiểm tra CI qua `After CI Checks Pass`. Đây là chức năng của hosting, **không phải cơ chế tích hợp sẵn của ChatGPT**.

## 3. Đăng ký lần đầu trong ChatGPT

1. Trong ChatGPT web, vào **Plugins** → **+** → **Add custom MCP server** (nếu tài khoản/workspace đủ quyền).
2. Đặt tên `CVNSS4.0 Knowledge Hub`.
3. Dán URL MCP HTTPS thật hoặc chọn Secure MCP Tunnel được cấu hình.
4. Chọn xác thực phù hợp (OAuth nếu ứng dụng lưu thông tin cá nhân/tài khoản), xem xét cảnh báo bảo mật.
5. Bấm **Create as a plugin**, duyệt các tool được phát hiện, cài plugin.
6. Nếu muốn đóng gói thêm kỹ năng `SKILL.md` vào **chính plugin MCP vừa tạo**, lấy ID kỹ thuật `plugin_asdk_app_...` từ URL trang plugin rồi chuyển ID và thư mục `integrations/chatgpt-plugin` cho `@plugin-creator` để **cập nhật plugin hiện có**, không tạo một plugin MCP trùng lặp. Giữ nguyên liên kết server và auth.
7. Trong hội thoại mới, gõ `@CVNSS4.0 Knowledge Hub`, yêu cầu gọi `cvnss_convert` hoặc `cvnss_sources`.

**Lưu ý gói:** quy trình tạo custom MCP và quyền tool thay đổi theo gói và chính sách workspace. Xem Help Center hiện hành. Tính năng MCP đầy đủ trên web không đương nhiên khả dụng với mọi gói cá nhân.

## 4. Sau khi kết nối

| Thay đổi trong GitHub | Tự động? | Việc người quản trị cần làm |
|---|---|---|
| Sửa converter hoặc xử lý thuật toán | Nếu host bật Git deploy | Kiểm thử CI, hệ thống host tự redeploy |
| Sửa tài liệu trong kho RAG | Không với v0.1 | Chạy ingestion + xuất bản index KB |
| Thêm tool MCP mới | Server cập nhật được; ChatGPT có thể chưa | Chọn **Refresh** trong ChatGPT Plugins; review quyền |
| Sửa skill `SKILL.md` | Không tự cập nhật bản plugin đã upload | Rebuild ZIP → cập nhật plugin/release mới |
| Tạo cá nhân hóa trên ChatGPT | Không tự chuyển L1–L3 | Cần API/bộ nhớ có phân quyền và đồng ý dữ liệu |

## 5. Quy tắc an toàn quan trọng

- Server `cvnss_hub.mcp_server --http` hiện cố ý không cho bind `0.0.0.0` nếu không có reverse proxy/tunnel bảo vệ. **Không gỡ chặn một cách tùy tiện**.
- Nếu muốn public endpoint có xác thực, cần thiết kế OAuth hoặc auth gateway tương thích ChatGPT trước khi công bố URL. Việc cho phép `--trusted-hostname` chỉ bảo vệ Host/Origin, **không** cung cấp auth.
- Bộ công cụ hiện chỉ đọc: convert, inspect, candidates, audit, self_test, sources, knowledge. Chưa có tool ghi tiến độ, đồng bộ người dùng, crawl thư viện, xây RAG.
- URL giả `https://ten-mien-thuc-te-cua-ban/mcp` trong hướng dẫn là ký hiệu minh họa, không phải host đang vận hành.

## Tài liệu tham khảo
- [OpenAI: Connect and test your plugin](https://developers.openai.com/plugins/deploy/connect-chatgpt)
- [OpenAI: Package your plugin (reuse existing MCP app ID)](https://developers.openai.com/plugins/build/plugins)
- [OpenAI: Connecting custom MCP servers](https://help.openai.com/en/articles/12584461-connecting-custom-mcp-servers-in-chatgpt)
- [Render: Automatic Git deploys](https://render.com/docs/deploys)
- [Render: Connect GitHub](https://render.com/docs/git-provider)

Mọi URL/server, connection ID và tài khoản cần được xác thực theo môi trường thực tế; không có lệnh nào trong repo có thể tự cài đặt/ủy quyền kết nối ChatGPT thay người dùng.
