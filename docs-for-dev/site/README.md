# CVNSS4.0 — Sổ tay mở

Trang hướng dẫn tiếng Việt, HTML/CSS/JS thuần, không cần Node hoặc bước cài gói.
Phong cách wiki cổ điển: chữ serif, nền giấy, mục lục bên trái, liên kết tra cứu,
không dùng font hoặc script từ dịch vụ ngoài.

## Build và xem tại máy

Từ gốc kho mã:

```sh
python scripts/build_cvnss_site.py
python -m http.server 8080 --directory dist/site
```

Mở cổng 8080 tại máy để xem. Builder kiểm tra liên kết nội bộ, các anchor và
10 chủ đề khớp registry. Nó đóng gói kỹ năng v0.2.0 và sao chép dữ liệu chuẩn từ
`cvnss_hub/` vào đầu ra `dist/site/`. Không sửa các tệp sinh ra bằng tay.
Tất cả tài nguyên dùng đường dẫn tương đối để chạy đúng dưới `/CVNSS40_Tutor/`.

## Xuất bản tại GitHub Pages

1. Đưa thay đổi mã nguồn lên nhánh `main` của `xulytiengviet/CVNSS40_Tutor`.
2. Trong repository → Settings → Pages → Build and deployment, chọn nguồn
   **GitHub Actions** (cần quyền quản trị thiết lập Pages).
3. Mở Actions → **CVNSS4.0 guide · GitHub Pages**; chạy workflow nếu chưa tự chạy.
4. Đợi job `build` và `deploy` thành công; kiểm tra URL do job deployment trả về.
   Với cấu hình project Pages mặc định, đích dự kiến là
   `https://xulytiengviet.github.io/CVNSS40_Tutor/`.

Workflow build cả pull request nhưng chỉ deploy từ nhánh `main`, qua push hoặc chạy thủ công. Không triển khai từ pull request. Pages chỉ host tài liệu và
file tải xuống; máy chủ Render MCP và DeepTutor REST triển khai độc lập.
Một lần build cục bộ không xác nhận website công khai đã cập nhật.

## Nội dung và hành vi

- Các bước Plugin / MCP / REST có tab, điều khiển bằng bàn phím; không có JS vẫn
  đọc được toàn bộ ba hướng dẫn.
- Tìm 10 chủ đề có hỗ trợ tiếng Việt không dấu, thông báo khi không có kết quả.
- Nút sao chép có thông báo, dự phòng chọn văn bản khi clipboard bị chặn.
- Không gửi truy vấn hoặc nội dung người dùng tới MCP/API từ website này.
- Giữ riêng địa chỉ GitHub Pages, endpoint MCP và các REST route xác thực.
- Nội dung ghi công theo yêu cầu: Long Ngo phát triển; Trần Tư Bình và Kiều
  Trường Lâm phát kiến CVNSS4.0. © 2026.
- MIT áp dụng cho HTML, CSS, JS và nội dung hướng dẫn mới trong thư mục này.
  Tệp tải plugin, dữ liệu nguồn và DeepTutor giữ giấy phép tương ứng;
  không thay giấy phép Apache-2.0 ở gốc kho mã.
