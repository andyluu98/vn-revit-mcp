# Bảo mật

## Báo lỗ hổng

Xin **không** mở Issue công khai cho lỗ hổng bảo mật. Dùng tính năng
[Report a vulnerability](https://github.com/andyluu98/vn-revit-mcp/security/advisories/new) của GitHub.

## Phạm vi thiết kế

- vn-revit-mcp chỉ chạy các script có sẵn trong gói (`src/vn_revit_mcp/revit_scripts/`) qua lệnh `pyrevit agent run`. Không có công cụ nào nhận mã nguồn từ AI.
- Không mở cổng mạng. Giao tiếp với client MCP qua stdio; với Revit qua CLI của pyRevit và đường ống nội bộ Windows của pyRevit.
- Lệnh gọi `pyrevit` dùng danh sách tham số cố định, không qua shell.
- Đầu vào được kiểm tra: id phần tử (số nguyên dương, tối đa 200), tên tham số (tối đa 120 ký tự, không ký tự điều khiển), hạng mục (`OST_...` hoặc danh sách cố định), bộ chọn Revit (chỉ chữ số).
- Excel chỉ ghi vào thư mục tuyệt đối trên máy, không ghi đường dẫn mạng, không ghi đè file có sẵn.
- Công cụ sửa mô hình mặc định chạy thử. Chạy thật vẫn cần người dùng bấm Giữ trong Revit (chế độ `ask` của pyRevit).

## Giới hạn

- Bảo vệ của pyRevit (hoàn tác, duyệt) chỉ bảo vệ mô hình, không phải hộp cát cho Python. Xem `docs/agent-runtime.md` của pyRevit.
- Dữ liệu mô hình mà công cụ trả về được gửi tới nhà cung cấp mô hình AI của người dùng.
