# Triển khai CVNSS4.0 MCP tự động: GitHub → Render → ChatGPT

Mục tiêu: GitHub là **nguồn mã duy nhất**; Render triển khai MCP khi CI của nhánh liên kết đạt; ChatGPT gọi công cụ qua **một URL HTTPS ổn định**, không phải cài lại plugin mỗi lần thay đổi thuật toán.

**Tình trạng:** Mã nguồn Docker, Render Blueprint và MCP ASGI đã có trong repo. Không có Render service, domain, GitHub deployment integration hay ChatGPT plugin nào được tạo hộ trong quá trình commit mã nguồn. Bước gắn tài khoản GitHub với Render và cấp quyền ChatGPT cần chính chủ hoàn tất.

## 1. Thành phần hệ thống

```text
GitHub xulytiengviet/CVNSS40_Tutor (main)
   ├── cvnss_hub/oracle/cvnss-converter.js    # Rule Oracle 5.0 audit-safe
   ├── cvnss_hub/mcp_server.py                 # 6 read-only MCP tools
   ├── cvnss_hub/hosted.py                     # ASGI + /healthz + rate-limiter
   ├── deploy/cvnss-mcp/Dockerfile             # Python + Node, standalone MCP
   ├── render.yaml                             # Render Blueprint, checksPass
   ├── .github/workflows/cvnss-hub.yml         # CI + plugin ZIP artifact
   └── integrations/chatgpt-plugin/            # Skill source / plugin metadata
              |
              | CI green + Git-connected Render autoDeployTrigger: checksPass
              v
    https://<ten-thuc-te>.onrender.com/mcp
              |
              | ChatGPT Plugins → + → Add custom MCP server → No authentication
              v
           @CVNSS4.0 Knowledge Hub
```

Đây là bản **public anonymous, read-only** để phục vụ quy tắc/chuyển đổi trên dữ liệu mà người dùng chủ động gửi. Không dùng để truy cập hồ sơ riêng, token hoặc bộ nhớ L1/L2/L3. Để hỗ trợ các thao tác riêng tư, phải bổ sung OAuth 2.1 theo đặc tả MCP và tách tài khoản người dùng.

## 2. Triển khai Render Blueprint (thao tác một lần)

1. Hợp nhất PR CVNSS4.0 vào `main` **sau khi CI xanh**.
2. Vào [Render Dashboard](https://dashboard.render.com/) và đăng nhập; liên kết GitHub trong **Account Settings → Connected Accounts**. Cấp quyền cho repository `xulytiengviet/CVNSS40_Tutor`.
3. Vào **Blueprints → New Blueprint Instance**; chọn repository trên. Render phát hiện file `render.yaml` ở root.
4. Đặt tên Blueprint tùy chọn, kiểm tra dịch vụ `cvnss40-mcp` chạy Docker, branch `main`, `healthCheckPath: /healthz`, `autoDeployTrigger: checksPass`.
5. Chọn gói Render phù hợp (dịch vụ cần có thời gian hoạt động đáp ứng mục đích); kiểm tra chính sách/bảng giá tại Render. Xác nhận **Apply**. Đây là hành động tạo tài nguyên trên tài khoản Render; GitHub repo không thực hiện thay bạn.
6. Khi build/deploy hoàn tất, vào service → **Events / Logs** kiểm tra 23/23 Oracle, chạy `GET https://<your-service>.onrender.com/healthz` để nhận `ok:true`.
7. Trong Render, sao chép **URL HTTPS thực** của service. MCP mặc định nằm tại `https://<your-service>.onrender.com/mcp`; không dùng URL dự đoán. Render cung cấp `RENDER_EXTERNAL_HOSTNAME` để máy chủ thiết lập Host allowlist.
8. Dùng MCP Inspector hoặc MCP client thử gọi `tools/list` và `cvnss_self_test`. Các yêu cầu POST MCP cần đúng header/JSON-RPC theo MCP protocol, không phải truy cập `/mcp` bằng GET trình duyệt rồi mong thấy trang web.

Để thêm domain riêng, cài domain trên Render rồi đặt `CVNSS_MCP_PUBLIC_HOSTNAME` thành hostname mà reverse proxy chuyển đến (và cấu hình Origin riêng nếu browser client có Origin). Không cấp phép `Host: *` hoặc `Origin: *`.

**Chú ý:** Render chạy container theo `PORT` mà nền tảng cấp và kiểm tra health `/healthz`. MCP sử dụng HTTP Streamable; code rate-limit theo tiến trình, không phải rate-limit toàn mạng. Giới hạn thêm trên edge/WAF nếu cho dùng đông người.

## 3. Kết nối ChatGPT (thao tác một lần)

1. Trong ChatGPT web, vào **Plugins → + → Add custom MCP server**.
2. Nhập tên `CVNSS4.0 Knowledge Hub`, và endpoint URL **thật** `https://<your-service>.onrender.com/mcp`.
3. Chọn **No authentication**, **chỉ đối với bản 6 công cụ công khai chỉ đọc**. Bản này không cung cấp tài khoản người dùng/ghi dữ liệu. Nếu triển khai phiên bản dùng bộ nhớ riêng, phải đổi sang OAuth và review lại quyền.
4. Đọc rủi ro, bấm xác nhận và **Create as a plugin**. Kiểm tra danh sách công cụ `cvnss_convert`, `cvnss_inspect`, `cvnss_candidates`, `cvnss_audit`, `cvnss_self_test`, `cvnss_sources`.
5. Cài plugin vào tài khoản/workspace nếu được cấp quyền. Trong chat gõ `@CVNSS4.0 Knowledge Hub` và hỏi: `Hãy gọi cvnss_convert với text="Tiếng Việt", mode="cqn"`.

**Quyền tài khoản:** custom MCP phụ thuộc kế hoạch ChatGPT và chính sách workspace; tính năng trên web không đồng nghĩa mọi tài khoản được cấp quyền tạo.

## 4. Đồng bộ khi GitHub thay đổi

| Thay đổi | Cơ chế đồng bộ |
|---|---|
| Sửa `cvnss-converter.js`, thêm test | Commit PR → CI → merge main → Render tự build/redeploy nếu checksPass |
| Thay đổi mô tả/tool MCP | Code tự triển khai; trong ChatGPT chọn **Refresh** tool metadata và kiểm duyệt quyền |
| Thay đổi `SKILL.md` và `plugin.json` | Chạy `py scripts/build_cvnss_chatgpt_plugin.py` → cập nhật phiên bản plugin đã lưu; không tự đổi skill cài trong ChatGPT |
| Thêm tài liệu SourceForge | Không tự thành RAG. Cần ingestion/index version riêng theo chính sách tác quyền |
| Bộ nhớ học tập/hồ sơ cá nhân | Không đồng bộ ở phiên bản này, cần OAuth + API + consent |

Nếu không muốn dùng Render, có thể đưa cùng Dockerfile lên dịch vụ khác hỗ trợ Docker + HTTPS + Git auto deploy. Khi đó cần cung cấp `CVNSS_MCP_PUBLIC_HOSTNAME` trong biến môi trường và làm tương đương `checksPass`.

## 5. Kiểm thử trước khi gửi ChatGPT

- Vào GitHub Actions xem workflow `CVNSS4.0 Hub smoke tests` (tự kiểm thử, đóng gói wheel + ZIP plugin và kiểm thử fail-closed của hosted app).
- Xem Render logs để xác nhận host nhận `GET /healthz` và không có `421 Invalid Host`.
- Gọi MCP tools từ Inspector qua endpoint HTTPS; chỉ cần một `tools/list` và một `cvnss_convert` là xác minh được kết nối từ client.
- Dùng ChatGPT gọi `@CVNSS4.0 Knowledge Hub`; so sánh kết quả Oracle `Tiếng Việt → Tizb Vidf`.
- Khi gặp HTTP `429`, chờ hết giới hạn. Khi gặp `421`, kiểm tra domain thực, `CVNSS_MCP_PUBLIC_HOSTNAME` và Host header. Khi `502`, kiểm tra image build/server bind `PORT`.

## 6. Bảo mật và quyền riêng tư

- `CVNSS_MCP_PUBLIC_ANONYMOUS=yes` là **opt-in công khai**, không có OAuth. Mọi người có Internet đều có thể truy vấn sáu tool. Không dùng cho thông tin nhạy cảm.
- Không lưu user text, API keys hay thông tin học tập lên GitHub. Tắt access-log ứng dụng; nhà cung cấp hosting vẫn có nhật ký hạ tầng theo chính sách của họ.
- Bộ converter giới hạn đầu vào (100.000 ký tự tổng, 200 ký tự cho inspect), timeout Node 15 giây; gateway giới hạn 60 yêu cầu/phút/mỗi instance theo mặc định. Các hạn mức có thể thay đổi, không bảo đảm chống DoS quy mô lớn.
- Server chỉ chấp nhận Host từ Render hostname thực hoặc hostname khai báo, đồng thời chống DNS rebinding. Không tắt host/origin kiểm tra để khắc phục lỗi triển khai.
- Sau này khi cần **đăng nhập học viên, đồng bộ L1/L2/L3, nạp tài liệu riêng, tạo bài tập có lưu kết quả**, hãy dùng OAuth 2.1, phân quyền, CSDL có backup và cơ chế đồng ý xử lý dữ liệu, thay vì mở rộng anonymous endpoint trực tiếp.

## Tài liệu
- [OpenAI: Connect custom MCP server](https://developers.openai.com/api/docs/guides/custom-mcp-server)
- [OpenAI: Authentication for plugin MCP](https://developers.openai.com/plugins/build/auth)
- [Render: Blueprints](https://render.com/docs/blueprint-spec)
- [Render: Automatic deploys](https://render.com/docs/deploys)
- [Render: RENDER_EXTERNAL_HOSTNAME](https://render.com/docs/environment-variables)
- [CVNSS4.0 ChatGPT Plugin guide](../../cvnss_hub/CHATGPT_PLUGIN.md)
