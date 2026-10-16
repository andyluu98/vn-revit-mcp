# vn-revit-mcp

MCP tiếng Việt cho **Autodesk Revit**: hỏi Claude (hoặc AI khác hỗ trợ MCP) về mô hình Revit đang mở. Có các việc: thống kê cửa, phòng, khối lượng tường, sàn, kết cấu, kiểm tra tham số thiếu, xuất bảng khối lượng ra Excel.

Chạy qua **pyRevit 7** (phần *agent runtime*). Mọi thao tác đi qua lớp bảo vệ của pyRevit: lệnh chỉ đọc luôn được hoàn tác, lệnh sửa phải được bấm **Giữ** ngay trong Revit.

> **Trạng thái: bản thử 0.1.0.** Mã đã qua các bài kiểm thử tự động với một `pyrevit` giả lập, nhưng **chưa chạy trên Revit thật**. Hãy thử trên mô hình mẫu trước, gặp lỗi xin mở [Issue](https://github.com/andyluu98/vn-revit-mcp/issues).

## Làm được gì

| Công cụ | Việc | Sửa mô hình? |
|---|---|---|
| `kiem_tra_ket_noi` | Kiểm tra pyRevit và các phiên Revit đang chạy | Không |
| `thong_tin_du_an` | Tên mô hình, bản Revit, các tầng và cao độ (m), view đang mở | Không |
| `dem_theo_hang_muc` | Đếm phần tử theo từng hạng mục | Không |
| `thong_ke_cua` | Cửa đi, cửa sổ theo family, loại, kích thước (mm), tầng; cửa chưa có ký hiệu | Không |
| `thong_ke_phong` | Phòng: số, tên, tầng, diện tích (m²), chu vi; phòng chưa đặt, chưa khép kín | Không |
| `khoi_luong_tuong` | Tường theo loại và tầng: dài (m), diện tích (m²), thể tích (m³), độ dày | Không |
| `khoi_luong_san` | Sàn theo loại và tầng: diện tích (m²), thể tích (m³), độ dày | Không |
| `khoi_luong_ket_cau` | Thể tích (m³) cột, dầm, móng theo vật liệu | Không |
| `kiem_tra_tham_so` | Phần tử chưa có hoặc để trống một tham số (ví dụ cửa thiếu Mark) | Không |
| `xuat_excel_khoi_luong` | Xuất Excel: bảng khối lượng (KL thiết kế, hao hụt, KL mua) và các sheet chi tiết | Không (chỉ ghi file Excel) |
| `dat_tham_so` | Gán giá trị một tham số cho tối đa 200 phần tử. Mặc định chỉ **chạy thử** | Có, sau khi bạn bấm Giữ trong Revit |

Số liệu được đổi từ đơn vị nội bộ của Revit (feet) sang m, m², m³, mm. Tổng được tính trên số đầy đủ, chỉ làm tròn 2 chữ số khi hiển thị.

## Cách hoạt động

```text
Claude Code / Claude Desktop / Cursor ...
        │  MCP (stdio)
        ▼
 vn-revit-mcp  (Python, chạy trên máy bạn)
        │  gọi lệnh: pyrevit agent run <script cố định>
        ▼
 pyRevit CLI ──(đường ống nội bộ Windows, không mở cổng mạng)──► pyRevit agent host trong Revit ──► Revit API
```

- vn-revit-mcp **chỉ chạy các script viết sẵn** trong gói, không có công cụ nào cho AI gửi code tùy ý.
- Cần cho AI tự viết code Revit thì dùng MCP gốc của pyRevit (`pyrevit mcp install claude`). Hai MCP dùng song song được.

## Yêu cầu

| Thứ | Ghi chú |
|---|---|
| Windows 10 hoặc 11 | Revit chỉ chạy trên Windows |
| Autodesk Revit | Nên dùng 2024 hoặc 2025: tài liệu pyRevit ghi agent runtime đã kiểm trên hai bản này |
| pyRevit **7.0 trở lên** | Bản có agent runtime, tải ở [pyRevit Releases](https://github.com/pyrevitlabs/pyRevit/releases) |
| uv | Trình cài gói Python, xem [hướng dẫn cài uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Claude Code hoặc client MCP khác | |

## Cài đặt

### Cách nhanh: nhờ Claude cài

Mở Claude Code, dán câu sau:

```text
Cài vn-revit-mcp cho tôi theo README ở https://github.com/andyluu98/vn-revit-mcp.
Kiểm tra máy đã có pyRevit 7 và uv chưa, thiếu thì hướng dẫn tôi từng bước vì tôi không rành terminal.
Bật agent host của pyRevit ở chế độ chỉ đọc (readonly), đăng ký MCP ở phạm vi user, rồi kiểm tra kết nối.
```

### Cách tự làm

1. **Cài pyRevit 7**: tải file `.exe` ở trang Releases, cài với lựa chọn mặc định.
2. **Bật agent host của pyRevit**, mở cửa sổ dòng lệnh mới rồi chạy:

   ```powershell
   pyrevit configs agent policy readonly
   pyrevit configs agent enable
   ```

   `readonly` chỉ cho đọc, dùng để làm quen. Khi cần sửa mô hình, đổi sang `ask` (mỗi lần sửa đều hỏi trong Revit): `pyrevit configs agent policy ask`.
3. **Khởi động lại Revit, mở một mô hình**, rồi kiểm tra:

   ```powershell
   pyrevit agent status
   ```

   Thấy phiên Revit của bạn trong danh sách là được.
4. **Đăng ký vào Claude Code**. Chạy trong cửa sổ dòng lệnh, không chạy trong Claude Code:

   ```powershell
   claude mcp add vn-revit -s user '--' uvx --from git+https://github.com/andyluu98/vn-revit-mcp vn-revit-mcp
   ```

   Trên PowerShell phải để `'--'` trong ngoặc đơn. Trên cmd hoặc bash thì viết `--` không cần ngoặc.

   Với Claude Desktop, thêm vào `claude_desktop_config.json`:

   ```json
   {
     "mcpServers": {
       "vn-revit": {
         "command": "uvx",
         "args": ["--from", "git+https://github.com/andyluu98/vn-revit-mcp", "vn-revit-mcp"]
       }
     }
   }
   ```

5. **Mở cuộc trò chuyện mới** trong Claude và hỏi: *"Kiểm tra kết nối Revit"*.

## Ví dụ câu hỏi

- "Mô hình đang mở có bao nhiêu cửa đi, cửa sổ? Chia theo tầng."
- "Tổng diện tích phòng từng tầng là bao nhiêu? Có phòng nào chưa khép kín không?"
- "Khối lượng tường xây theo loại tường và tầng."
- "Cửa nào chưa có Mark?"
- "Xuất bảng khối lượng ra Excel vào thư mục D:\DuAn\NhaPho\KhoiLuong."
- "Chạy thử: ghi Comments = 'Kiểm tra PCCC' cho các cửa id 12345, 12346."

## File Excel

- Lưu vào thư mục bạn chọn, hoặc `Documents\vn-revit-mcp` nếu không chọn.
- Tên file dạng `01_khoi-luong-revit-<ten-mo-hinh>.xlsx`, số tăng dần, **không bao giờ ghi đè** file cũ.
- **Sheet `KhoiLuong`:** các cột STT, Mã hiệu, Tên công việc, Đơn vị, Diễn giải, KL thiết kế, Hao hụt (%), KL hao hụt, KL mua, Nguồn.
  - Ô **Hao hụt (%)** để trống, tô vàng, để kỹ sư điền theo định mức. KL hao hụt và KL mua tự tính bằng công thức.
  - **Mã hiệu** ghi `[Chờ bổ sung]`.
- **Sheet chi tiết:** `Tuong`, `San`, `KetCau`, `Cua`, `Phong`.
- **Sheet `Nguon`:** mô hình, bản Revit, thời điểm trích và các lưu ý.
- **Giới hạn:** khối lượng phụ thuộc cách dựng mô hình (join, giao cắt, vật liệu). Luôn đối chiếu bản vẽ trước khi dùng cho hợp đồng.

## An toàn và dữ liệu

- **Không mở cổng mạng.** vn-revit-mcp nói chuyện với AI qua stdio, với Revit qua lệnh `pyrevit`, và lệnh này đi qua đường ống nội bộ chỉ tài khoản Windows của bạn dùng được.
- **Không có công cụ chạy code tùy ý.** Mọi script nằm sẵn trong gói và được kiểm thử. Các tham số AI truyền vào đều bị kiểm tra: id phải là số nguyên dương, tối đa 200; tên tham số tối đa 120 ký tự; hạng mục phải là `OST_...` hoặc tên trong danh sách.
- **Lệnh sửa có hai lớp chặn.** Mặc định chỉ chạy thử. Khi chạy thật, Revit vẫn hỏi Giữ/Hủy, trừ khi bạn đặt pyRevit ở chế độ `auto`; **không nên** dùng `auto` với mô hình thật.
- **Dữ liệu mô hình đi ra ngoài máy.** Những gì công cụ trả về (tên loại, tầng, tham số...) được gửi tới nhà cung cấp mô hình AI bạn đang dùng. Kiểm tra quy định bảo mật của dự án trước khi dùng với hồ sơ khách.
- **pyRevit lưu lại từng lần chạy.** Script, kết quả và ảnh được lưu dạng văn bản rõ (không mã hóa) trong thư mục dữ liệu của pyRevit, tối đa 14 ngày (theo tài liệu pyRevit).

Báo lỗ hổng bảo mật: xem [SECURITY.md](SECURITY.md).

## Xử lý lỗi

| Mã lỗi | Nghĩa | Cách xử lý |
|---|---|---|
| `cli_not_found` | Không thấy lệnh `pyrevit` | Cài pyRevit 7, mở cửa sổ dòng lệnh mới; hoặc đặt biến `VN_REVIT_MCP_PYREVIT` trỏ tới `pyrevit.exe` |
| `no_instance` | Không có Revit nào bật agent host | `pyrevit configs agent enable`, khởi động lại Revit, mở mô hình |
| `revit_busy` | Revit đang bận hoặc có hộp thoại mở | Đóng hộp thoại, chờ lệnh khác chạy xong |
| `no_active_document` | Chưa mở mô hình | Mở một mô hình trong Revit |
| `timeout`, `cli_timeout` | Chạy quá lâu | Thử mô hình nhỏ hơn, kiểm tra Revit có treo không |
| `dau_vao_khong_hop_le` | Tham số AI truyền vào sai | Xem `thong_bao` |

Mở nhiều Revit cùng lúc: mọi công cụ nhận tham số `revit` (năm, ví dụ `2025`, hoặc số process). Đặt mặc định bằng biến môi trường `VN_REVIT_MCP_REVIT`.

## Phát triển

```powershell
git clone https://github.com/andyluu98/vn-revit-mcp
cd vn-revit-mcp
uv sync
uv run pytest
```

Kiểm thử dùng `tests/fake_pyrevit.py`, một lệnh `pyrevit` giả trả JSON đúng dạng pyRevit 7. Vì vậy không cần Revit để chạy kiểm thử. Script trong `src/vn_revit_mcp/revit_scripts/` phải giữ cú pháp chạy được trên IronPython 2.7 (engine mặc định của pyRevit) và chỉ dùng ký tự ASCII; kiểm thử tự kiểm hai điều này.

## Liên quan đến pyRevit

vn-revit-mcp là dự án độc lập, không thuộc pyRevitLabs. Dự án gọi lệnh `pyrevit` đã cài trên máy bạn và không chép mã nguồn của pyRevit. pyRevit có giấy phép GPL-3.0 riêng; vn-revit-mcp dùng giấy phép [MIT](LICENSE).

## Nguồn tham khảo (tra ngày 16/10/2026)

- pyRevit agent runtime: `docs/agent-runtime.md` trong repo [pyrevitlabs/pyRevit](https://github.com/pyrevitlabs/pyRevit)
- Lệnh `pyrevit agent run` và dạng JSON trả về: `dev/pyRevitLabs/pyRevitCLI/PyRevitCLIAgentCmds.cs`, `dev/pyRevitLabs.PyRevit.Runtime/Agent/AgentRunService.cs`
- pyRevit v7.0.0 phát hành ngày 06/10/2026: [Release notes](https://github.com/pyrevitlabs/pyRevit/releases)
