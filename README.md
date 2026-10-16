# vn-revit-mcp

Bộ công cụ tiếng Việt để dùng **Claude** (hoặc AI khác hỗ trợ MCP) với **Autodesk Revit**, gồm hai phần:

| Phần | Làm gì | Chạy bằng |
|---|---|---|
| **A. Vẽ, dựng mô hình** | Claude dựng tầng, tường, phòng, sàn, cửa, cột, mái từ mô tả hoặc từ bản vẽ AutoCAD | MCP có sẵn của **pyRevit 7** + skill tiếng Việt **`ve-revit`** trong repo này |
| **B. Thống kê, khối lượng** | Thống kê cửa, phòng; khối lượng tường, sàn, kết cấu; kiểm tham số thiếu; xuất Excel | MCP **vn-revit-mcp** trong repo này |

Hai phần chạy song song: Claude dùng phần A để dựng, rồi dùng phần B để kiểm lại khối lượng vừa dựng.

> **Trạng thái: bản thử 0.2.0.** Hãy thử trên một mô hình nháp trước. Gặp lỗi xin mở [Issue](https://github.com/andyluu98/vn-revit-mcp/issues).

---

## Mục lục

1. [Cách hoạt động](#1-cách-hoạt-động)
2. [Yêu cầu](#2-yêu-cầu)
3. [Cài đặt](#3-cài-đặt)
4. [Vẽ trên Revit bằng Claude](#4-vẽ-trên-revit-bằng-claude)
5. [Thống kê và khối lượng](#5-thống-kê-và-khối-lượng)
6. [An toàn và dữ liệu](#6-an-toàn-và-dữ-liệu)
7. [Xử lý lỗi](#7-xử-lý-lỗi)
8. [Gỡ cài đặt](#8-gỡ-cài-đặt)
9. [Phát triển](#9-phát-triển)
10. [Liên quan đến pyRevit và nguồn tham khảo](#10-liên-quan-đến-pyrevit-và-nguồn-tham-khảo)

---

## 1. Cách hoạt động

```text
                     Claude Code / Claude Desktop / Cursor ...
                       │                              │
          MCP "pyrevit" (vẽ)                MCP "vn-revit" (thống kê)
          + skill ve-revit                            │
                       │                              │ gọi lệnh: pyrevit agent run <script cố định>
                       ▼                              ▼
                 pyRevit CLI ──(đường ống nội bộ Windows, không mở cổng mạng)──►
                 pyRevit agent host trong Revit ──► Revit API ──► mô hình đang mở
```

**Phần A, vẽ:** Claude tự viết một đoạn Python dùng Revit API (ví dụ "tạo 4 bức tường 200 quanh lô 5x15 m") rồi gửi qua công cụ `run_modify` của pyRevit. pyRevit chạy đoạn code đó bên trong Revit, gom mọi thay đổi vào một nhóm, rồi hiện hộp **Keep / Discard** ngay trong Revit. Bạn bấm Keep thì thay đổi được lưu thành một mục Undo; bấm Discard thì mô hình trở lại như cũ.

Skill `ve-revit` là "sổ tay" dạy Claude làm việc này theo cách của người Việt: số liệu mm, cốt ±0.000 tại sàn tầng 1, dựng từng chặng, chạy thử trước khi chạy thật, tra loại tường, cửa có sẵn trong mô hình thay vì đoán tên, không tự bịa kích thước.

**Phần B, thống kê:** vn-revit-mcp chỉ chạy 9 script viết sẵn trong gói. AI không gửi code tùy ý qua phần này được. 10 trên 11 công cụ chỉ đọc mô hình.

## 2. Yêu cầu

| Thứ | Ghi chú |
|---|---|
| Windows 10 hoặc 11 | Revit chỉ chạy trên Windows |
| Autodesk Revit | Nên dùng **2024 hoặc 2025**: tài liệu pyRevit ghi agent runtime đã kiểm trên hai bản này |
| pyRevit **7.0 trở lên** | Bản có agent runtime và MCP, tải ở [pyRevit Releases](https://github.com/pyrevitlabs/pyRevit/releases) |
| uv | Trình cài gói Python, xem [hướng dẫn cài uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Claude Code | Hoặc Claude Desktop, Cursor, VS Code, Codex |
| Một mô hình Revit có sẵn loại tường, sàn, family cửa | Nên mở từ template kiến trúc. Skill không tự tải family |

## 3. Cài đặt

### 3.1. Cách nhanh: nhờ Claude cài

Mở Claude Code và dán câu sau:

```text
Cài bộ vn-revit-mcp cho tôi theo README ở https://github.com/andyluu98/vn-revit-mcp, mục 3.2, đủ 8 bước.
Kiểm tra máy đã có pyRevit 7 và uv chưa; thiếu thì hướng dẫn tôi từng bước vì tôi không rành terminal.
Đặt pyRevit ở chế độ ask (mỗi lần sửa mô hình đều hỏi tôi trong Revit). Không dùng chế độ auto.
Làm xong thì nhắc tôi khởi động lại Revit và Claude Code, rồi kiểm tra kết nối.
```

### 3.2. Cách tự làm

Các lệnh dưới đây chạy trong **PowerShell** (bấm Start, gõ PowerShell). Mỗi khi cài thêm chương trình, nên mở cửa sổ PowerShell mới.

**Bước 1. Cài pyRevit 7.** Tải file `.exe` ở [trang Releases](https://github.com/pyrevitlabs/pyRevit/releases), cài với lựa chọn mặc định. Kiểm tra:

```powershell
pyrevit --version
```

**Bước 2. Bật agent host và đặt chế độ hỏi trước khi sửa:**

```powershell
pyrevit configs agent enable
pyrevit configs agent policy ask
```

| Chế độ | Nghĩa |
|---|---|
| `readonly` | Chỉ đọc, chạy thử. Không sửa được mô hình |
| `ask` (nên dùng) | Mỗi lần sửa, Revit hiện hộp Keep / Discard để bạn quyết |
| `auto` | Sửa luôn, không hỏi. **Không nên dùng** với mô hình thật |

**Bước 3. Đăng ký MCP của pyRevit (phần vẽ) vào Claude Code:**

```powershell
pyrevit mcp install claude
```

Dùng client khác thì thay `claude` bằng `codex`, `cursor`, `vscode` hoặc `opencode`. Với Claude Desktop, thêm vào `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pyrevit": { "command": "pyrevit", "args": ["mcp"] }
  }
}
```

**Bước 4. Đăng ký vn-revit-mcp (phần thống kê):**

```powershell
claude mcp add vn-revit -s user '--' uvx --from git+https://github.com/andyluu98/vn-revit-mcp vn-revit-mcp
```

Trên PowerShell phải để `'--'` trong ngoặc đơn. Trên cmd hoặc bash thì viết `--` không cần ngoặc. Với Claude Desktop, thêm vào cùng file cấu hình:

```json
"vn-revit": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/andyluu98/vn-revit-mcp", "vn-revit-mcp"]
}
```

**Bước 5. Cài skill `ve-revit`** cho cả Claude Code và pyRevit, kèm thư mục dữ liệu mặt bằng mẫu:

```powershell
uvx --from git+https://github.com/andyluu98/vn-revit-mcp vn-revit-mcp cai-skill --workspace D:\DuAn\revit-workspace
```

Lệnh này chép skill vào:

| Nơi | Ai đọc |
|---|---|
| `%USERPROFILE%\.claude\skills\ve-revit` | Claude Code |
| `%APPDATA%\pyRevit\agent\skills\ve-revit` | Công cụ `get_skill` của MCP pyRevit |
| Thư mục `--workspace` (tùy chọn) | Dữ liệu mặt bằng mẫu `nha_pho_mau.py` và hàm đổi đơn vị `vn_don_vi.py` |

Đã có bản cũ khác nội dung thì bản cũ được **chuyển** vào `Documents\vn-revit-mcp\_backup`, không bị xóa. File đã có trong thư mục workspace thì giữ nguyên.

**Bước 6. Cho pyRevit đọc skill của người dùng:**

```powershell
pyrevit configs agent skills enable
```

**Bước 7. Cho Claude Code chờ lâu hơn** khi bạn đang xem hộp Keep / Discard. Mặc định Claude Code có thể bỏ cuộc trước khi bạn kịp bấm. Đặt 10 phút:

```powershell
setx MCP_TOOL_TIMEOUT 600000
```

**Bước 8. Khởi động lại Revit, mở một mô hình, khởi động lại Claude Code.** Kiểm tra:

```powershell
pyrevit agent status
claude mcp list
```

Thấy phiên Revit trong danh sách đầu, thấy `pyrevit` và `vn-revit` ở danh sách sau là xong. Mở cuộc trò chuyện mới và hỏi: *"Kiểm tra kết nối Revit"*.

## 4. Vẽ trên Revit bằng Claude

### 4.1. Quy trình một lần dựng

```text
 1. Bạn đưa yêu cầu: mô tả, ảnh, PDF hoặc DWG mặt bằng
 2. Claude đọc get_context (Revit nào, mô hình nào, chế độ ask chưa)
 3. Claude tra loại tường, sàn, cửa, tầng có sẵn trong mô hình
 4. Claude ghi số liệu mặt bằng (mm) vào nha_pho_mau.py trong thư mục workspace, chạy kiem_tra()
 5. Mỗi chặng: chạy thử (dry run) → báo số phần tử → chạy thật → bạn bấm Keep / Discard trong Revit
 6. Claude chụp ảnh 3D, mặt bằng để tự kiểm
 7. Claude gọi vn-revit-mcp đối chiếu khối lượng với số liệu ban đầu
```

Thứ tự chặng: **tầng → tường → phòng → sàn → cửa đi, cửa sổ → cột, dầm, mái, cầu thang.** Mỗi chặng là một mục Undo riêng; chặng sau lỗi không làm mất chặng trước. Mọi phần tử Claude tạo đều được ghi Comments dạng `vn:<chặng>` để chạy lại chặng đó mà không bị trùng.

### 4.2. Câu lệnh mẫu

**Dựng từ mô tả:**

```text
Dùng skill ve-revit. Dựng nhà phố 2 tầng trên lô 5x15 m trong mô hình Revit đang mở:
tầng cao 3600, tường bao 200, tường ngăn 100. Tầng 1: phòng khách phía trước sâu 6 m, bếp ăn,
cuối nhà WC và kho. Tầng 2: hai phòng ngủ. Cửa chính rộng 2400 ở mặt tiền.
Làm từng chặng, chạy thử trước, chờ tôi bấm Keep rồi mới làm chặng sau.
```

**Dựng từ bản vẽ AutoCAD:**

```text
Dùng skill ve-revit. Đọc mặt bằng tầng 1 và tầng 2 trong D:\DuAn\NhaPho\KT-02.pdf (hoặc file .dwg).
Ghi số liệu vào D:\DuAn\revit-workspace\nha_pho_mau.py, chạy kiem_tra(), báo tôi chỗ bản vẽ lệch
trước khi dựng. Chưa dựng gì khi tôi chưa duyệt bảng số liệu.
```

**Sửa một phần:**

```text
Dùng skill ve-revit. Dời cửa D2 tầng 1 sang phải 300 mm và đổi sang cửa 800x2200.
Chạy thử, báo trước khi chạy thật.
```

**Kiểm sau khi dựng:**

```text
Dùng vn-revit: tổng chiều dài tường 200 và 100 từng tầng, diện tích từng phòng,
số cửa theo kích thước. So với nha_pho_mau.py và báo chỗ lệch.
```

### 4.3. Dữ liệu mặt bằng trong workspace

Claude không dán lại số liệu vào mỗi đoạn code. Số liệu nằm trong một file Python ở thư mục workspace, mỗi lần chạy pyRevit nạp lại file đó. Bạn mở `nha_pho_mau.py` bằng Notepad là đọc được:

```python
TANG = [("Tang 1", 0), ("Tang 2", 3600), ("Mai", 7200)]

TUONG = [
    {"ten": "T1-truoc", "tu": (0, 0), "den": (5000, 0), "day": 200, "tang": "Tang 1", "den_tang": "Tang 2"},
    ...
]
CUA = [
    {"loai": "cua_di", "ky_hieu": "D1", "tuong": "T1-truoc", "vi_tri": (2500, 0), "rong": 2400, "cao": 2600, "cao_be": 0},
    ...
]
```

- Đơn vị **mm**, gốc tọa độ tại giao trục góc trước bên trái, trục x dọc mặt tiền, trục y vào sâu.
- Tường ghi theo **trục tường**. Cửa ghi tọa độ điểm giữa cửa nằm trên trục tường.
- `kiem_tra()` báo lỗi trước khi dựng: tầng không có, tường dài bằng 0, cửa lệch trục tường, cửa quá sát chỗ giao tường (Revit cần ít nhất nửa bề rộng cửa cộng 152 mm), số phòng trùng.
- File mẫu là **nhà phố mẫu 5x15 m**, chỉ để minh họa cách ghi, không phải công trình thật.

### 4.4. Công cụ của MCP pyRevit

Theo tài liệu pyRevit 7 (`docs/agent-runtime.md`):

| Công cụ | Sửa mô hình | Dùng để |
|---|---|---|
| `get_context` | Không | Bản Revit, mô hình, view, chọn, tầng, chế độ policy, engine Python |
| `get_skill`, `list_skills` | Không | Đọc skill hướng dẫn (có `ve-revit` sau bước 5, 6) |
| `inspect_elements` | Không | Xem tham số, vị trí của tối đa 50 phần tử |
| `lookup_revit_api` | Không | Tra tên hàm, lớp Revit API ngay trong Revit đang chạy |
| `run_query` | Không bao giờ | Chạy script chỉ đọc; thay đổi luôn bị hoàn tác |
| `run_modify` | Sau khi bạn bấm Keep | Chạy script sửa mô hình; `dry_run=true` để xem trước |
| `capture_view` | Không | Chụp ảnh view, 3D để Claude tự xem kết quả |
| `show_elements` | Không | Chọn, zoom, cô lập tạm phần tử trong view |
| `get_run` | Không | Xem lại một lần chạy đã ghi |

### 4.5. Giới hạn cần biết

- **Family phải có sẵn trong mô hình.** Không có cửa đúng kích thước, Claude sẽ hỏi bạn nạp family hoặc nhân bản type. Skill không tự tải family từ Internet.
- **Tên loại khác nhau giữa các template.** Claude luôn tra tên trong mô hình, không dùng tên nhớ sẵn.
- **Cầu thang, mái phức tạp dễ lỗi hơn tường, sàn.** Nên dựng riêng, kiểm kỹ.
- **Mô hình dựng theo dữ liệu, không thay kiến trúc sư, kỹ sư.** Hồ sơ xin phép, thi công phải được người có chứng chỉ kiểm tra.

## 5. Thống kê và khối lượng

| Công cụ | Việc | Sửa mô hình? |
|---|---|---|
| `kiem_tra_ket_noi` | Kiểm tra pyRevit và các phiên Revit đang chạy | Không |
| `thong_tin_du_an` | Tên mô hình, bản Revit, các tầng và cao độ (m), view đang mở | Không |
| `dem_theo_hang_muc` | Đếm phần tử theo từng hạng mục | Không |
| `thong_ke_cua` | Cửa đi, cửa sổ theo family, loại, kích thước (mm), tầng; cửa chưa có ký hiệu | Không |
| `thong_ke_phong` | Phòng: số, tên, tầng, diện tích (m²), chu vi; phòng chưa đặt, chưa khép kín | Không |
| `khoi_luong_tuong` | Tường theo loại và tầng: dài (m), diện tích (m²), thể tích (m³), độ dày; vách kính tính riêng | Không |
| `khoi_luong_san` | Sàn theo loại và tầng: diện tích (m²), thể tích (m³), độ dày | Không |
| `khoi_luong_ket_cau` | Thể tích (m³) cột, dầm, móng theo vật liệu | Không |
| `kiem_tra_tham_so` | Phần tử chưa có hoặc để trống một tham số (ví dụ cửa thiếu Mark) | Không |
| `xuat_excel_khoi_luong` | Xuất Excel: bảng khối lượng và các sheet chi tiết | Không (chỉ ghi file Excel) |
| `dat_tham_so` | Gán giá trị một tham số cho tối đa 200 phần tử. Mặc định chỉ **chạy thử** | Có, sau khi bạn bấm Keep |

Số liệu đổi từ đơn vị nội bộ của Revit (feet) sang m, m², m³, mm. Tổng tính trên số đầy đủ, chỉ làm tròn 2 chữ số khi hiển thị.

**Câu hỏi mẫu:**

- "Mô hình đang mở có bao nhiêu cửa đi, cửa sổ? Chia theo tầng."
- "Tổng diện tích phòng từng tầng? Có phòng nào chưa khép kín không?"
- "Cửa nào chưa có Mark?"
- "Xuất bảng khối lượng ra Excel vào D:\DuAn\NhaPho\KhoiLuong."
- "Chạy thử: ghi Comments = 'Kiểm tra PCCC' cho các cửa id 12345, 12346."

**File Excel:**

- Lưu vào thư mục bạn chọn, hoặc `Documents\vn-revit-mcp` nếu không chọn. Tên `01_khoi-luong-revit-<ten-mo-hinh>.xlsx`, số tăng dần, **không bao giờ ghi đè**.
- Sheet `KhoiLuong`: STT, Mã hiệu, Tên công việc, Đơn vị, Diễn giải, KL thiết kế, Hao hụt (%), KL hao hụt, KL mua, Nguồn. Ô Hao hụt (%) để trống, tô vàng cho kỹ sư điền; KL hao hụt và KL mua tự tính bằng công thức. Mã hiệu ghi `[Chờ bổ sung]`. Dòng nào Revit không trả khối lượng thì Diễn giải ghi "Cần xác nhận lại".
- Sheet chi tiết `Tuong`, `San`, `KetCau`, `Cua`, `Phong`; sheet `Nguon` ghi mô hình, bản Revit, thời điểm trích và các lưu ý.
- Khối lượng phụ thuộc cách dựng mô hình. Phần giao giữa các cấu kiện chưa join bị tính hai lần. Luôn đối chiếu bản vẽ trước khi dùng cho hợp đồng.

## 6. An toàn và dữ liệu

**Phần A (vẽ) chạy code do AI viết, có toàn quyền như tài khoản Windows của bạn.** pyRevit bảo vệ **mô hình** (gom thay đổi, chặn lưu file trong lúc chạy, hỏi Keep / Discard) nhưng **không phải hộp cát**: đoạn code vẫn đọc, ghi được file trên máy. Vì vậy:

- Chỉ dùng với AI client bạn tin cậy. Không đưa cho Claude tài liệu lạ có chứa câu lệnh (file tải từ nguồn không rõ, email lạ) rồi để nó dựng mô hình.
- Giữ chế độ `ask`. Đọc tóm tắt chạy thử trước khi bấm Keep.
- Làm trên bản sao mô hình khi mới dùng.

**Phần B (thống kê):**

- Không có công cụ chạy code tùy ý: chỉ 9 script cố định, đã kiểm thử.
- Tham số AI truyền vào đều bị kiểm: id là số nguyên dương, tối đa 200; tên tham số tối đa 120 ký tự; hạng mục phải là `OST_...` hoặc tên trong danh sách; chỉ gọi `pyrevit.exe`, không gọi file `.bat`, `.cmd`.
- Tên lấy từ mô hình không bao giờ được ghi thành công thức trong Excel.

**Chung cho cả hai phần:**

- **Không mở cổng mạng.** Lệnh `pyrevit` nói chuyện với Revit qua đường ống nội bộ chỉ tài khoản Windows của bạn dùng được.
- **Dữ liệu mô hình đi ra ngoài máy.** Những gì công cụ trả về (tên loại, tầng, tham số...) được gửi tới nhà cung cấp mô hình AI bạn đang dùng. Kiểm tra quy định bảo mật của dự án trước khi dùng với hồ sơ khách.
- **pyRevit lưu lại từng lần chạy.** Script, đầu vào, kết quả, ảnh chụp được lưu dạng văn bản rõ trong `%APPDATA%\pyRevit\agent`, tối đa 14 ngày.

Báo lỗ hổng bảo mật: xem [SECURITY.md](SECURITY.md).

## 7. Xử lý lỗi

| Lỗi | Nghĩa | Cách xử lý |
|---|---|---|
| `cli_not_found` | Không thấy lệnh `pyrevit` | Cài pyRevit 7, mở PowerShell mới; hoặc đặt biến `VN_REVIT_MCP_PYREVIT` trỏ tới `pyrevit.exe` |
| `no_instance` | Không có Revit nào bật agent host | `pyrevit configs agent enable`, khởi động lại Revit, mở mô hình |
| `revit_busy` | Revit đang bận hoặc có hộp thoại mở | Đóng hộp thoại (kể cả nhắc lưu file), chờ lệnh khác xong |
| `no_active_document` | Chưa mở mô hình | Mở một mô hình trong Revit |
| `policy_readonly` | pyRevit đang chỉ đọc | `pyrevit configs agent policy ask` |
| `approval_timeout` | Hết giờ chờ trong lúc hộp Keep / Discard còn mở | Xem danh sách Undo trong Revit trước khi chạy lại; tăng `MCP_TOOL_TIMEOUT` (bước 7) |
| `ambiguous_revit` | Đang mở nhiều Revit | Ghi rõ năm Revit trong câu hỏi, hoặc đặt biến `VN_REVIT_MCP_REVIT=2025` |
| `revit_failure` | Revit báo lỗi khi dựng (ví dụ cửa không cắt được tường) | Thường do cửa quá sát chỗ giao tường hoặc rộng hơn đoạn tường: sửa dữ liệu, chạy `kiem_tra()` |
| `transaction_left_open` | Đoạn code quên đóng transaction | Nhờ Claude sửa script và chạy lại; mô hình đã được hoàn tác |
| `timeout`, `cli_timeout` | Chạy quá lâu | Chia nhỏ chặng, kiểm tra Revit có treo không |
| `dau_vao_khong_hop_le` | Tham số truyền vào vn-revit-mcp sai | Xem `thong_bao` |
| Claude không thấy skill `ve-revit` | Chưa cài hoặc chưa bật | Làm lại bước 5, 6; khởi động lại Claude Code và Revit |

## 8. Gỡ cài đặt

```powershell
claude mcp remove vn-revit -s user
pyrevit mcp uninstall claude
pyrevit configs agent disable
```

Skill nằm ở `%USERPROFILE%\.claude\skills\ve-revit` và `%APPDATA%\pyRevit\agent\skills\ve-revit`; muốn bỏ thì xóa hai thư mục này bằng tay.

## 9. Phát triển

```powershell
git clone https://github.com/andyluu98/vn-revit-mcp
cd vn-revit-mcp
uv sync
uv run pytest
```

| Thư mục | Nội dung |
|---|---|
| `src/vn_revit_mcp/server.py` | MCP server và 11 công cụ |
| `src/vn_revit_mcp/revit_scripts/` | Script chạy trong Revit: chỉ cú pháp IronPython 2.7, chỉ ký tự ASCII |
| `src/vn_revit_mcp/skills/ve-revit/` | Skill dựng mô hình và workspace mẫu |
| `src/vn_revit_mcp/cai_skill.py` | Lệnh `vn-revit-mcp cai-skill` |
| `tests/fake_pyrevit.py` | Lệnh `pyrevit` giả trả JSON đúng dạng pyRevit 7, để kiểm thử không cần Revit |

Kiểm thử tự kiểm cú pháp IronPython 2.7, ký tự ASCII của script và workspace, tính nhất quán của dữ liệu mẫu, và việc cài skill không bao giờ xóa bản cũ.

## 10. Liên quan đến pyRevit và nguồn tham khảo

vn-revit-mcp là dự án độc lập, không thuộc pyRevitLabs. Dự án gọi lệnh `pyrevit` đã cài trên máy và không chép mã nguồn của pyRevit. pyRevit có giấy phép GPL-3.0 riêng; vn-revit-mcp dùng giấy phép [MIT](LICENSE).

Nguồn (tra ngày 16/10/2026, bản pyRevit `v7.0.0.26278+2233` phát hành 06/10/2026):

- Agent runtime, công cụ MCP, cấu hình, giới hạn: `docs/agent-runtime.md` trong repo [pyrevitlabs/pyRevit](https://github.com/pyrevitlabs/pyRevit)
- Skill gốc dựng mô hình: `pyrevitlib/pyrevit/agent/skills/modeling/SKILL.md`
- Hàm dựng `create_wall`, `create_floor`, `create_room`, `place_hosted_instance`: `pyrevitlib/pyrevit/revit/db/create.py`
- Lệnh `pyrevit agent run` và dạng JSON trả về: `dev/pyRevitLabs/pyRevitCLI/PyRevitCLIAgentCmds.cs`, `dev/pyRevitLabs.PyRevit.Runtime/Agent/AgentRunService.cs`
- [pyRevit Releases](https://github.com/pyrevitlabs/pyRevit/releases)
