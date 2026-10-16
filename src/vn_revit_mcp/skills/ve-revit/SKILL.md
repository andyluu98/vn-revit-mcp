---
name: ve-revit
description: Dựng mô hình nhà ở Việt Nam trong Revit qua MCP của pyRevit (run_modify) theo quy ước Việt Nam - số liệu mm, cốt ±0.000 tại sàn tầng 1, dựng theo từng chặng có chạy thử, tra loại tường, cửa có sẵn trong mô hình, kiểm lại bằng vn-revit-mcp. Dùng khi người dùng nói "vẽ nhà trên Revit", "dựng tường, sàn, cửa", "dựng mô hình từ bản vẽ AutoCAD".
---

# Dựng mô hình nhà ở trong Revit

Skill này dùng cùng **MCP của pyRevit** (công cụ `get_context`, `run_query`, `run_modify`,
`capture_view`, `lookup_revit_api`) và **vn-revit-mcp** (kiểm khối lượng sau khi dựng).

Trả lời người dùng bằng tiếng Việt, câu ngắn. Phần xây dựng dùng thẳng thuật ngữ ngành.

## 1. Trước khi viết script

1. Gọi `get_context`. Kiểm:
   - Có mô hình đang mở (`document` khác null). Không có thì nhờ người dùng mở mô hình.
   - `policy` là `ask`. Nếu `readonly` thì báo: chạy `pyrevit configs agent policy ask` trong
     cửa sổ dòng lệnh rồi thử lại. Không đề nghị `auto`.
   - `scripting.default_engine` và cú pháp Python tương ứng. IronPython 2.7 không có f-string.
2. Đọc skill gốc của pyRevit: `get_skill("revit-scripting")`, `get_skill("modeling")`.
   Skill này chỉ bổ sung quy ước Việt Nam, không thay skill gốc.
3. **Lấy số liệu từ bản vẽ, không tự nghĩ ra.** Kích thước, số tầng, chiều cao tầng, vị trí
   cửa lấy từ bản vẽ, PDF hoặc lời người dùng. Thiếu thì hỏi, mỗi lần một câu, kèm 2 đến 4
   phương án. Bản vẽ tự mâu thuẫn (tổng kích thước chi tiết khác kích thước tổng) thì báo chỗ
   lệch, hỏi lấy bên nào.
4. **Tra loại có sẵn trong mô hình** bằng một `run_query` (mẫu ở skill `modeling`): loại tường,
   loại sàn, family cửa đi, cửa sổ, cột, tầng hiện có. Chọn loại theo độ dày, kích thước.
   - Không có loại tường đúng độ dày: hỏi người dùng chọn loại gần nhất hay nhân bản loại
     (`WallType.Duplicate`) rồi sửa lớp kết cấu.
   - Không có family cửa đúng kích thước: hỏi người dùng nạp family hoặc nhân bản type rồi sửa
     tham số Width, Height. Không tự tải family từ Internet.

## 2. Dữ liệu mặt bằng nằm trong workspace

- Chép thư mục `workspace-mau` của skill này sang thư mục dự án của người dùng (ví dụ
  `D:\DuAn\NhaPho\revit-workspace`). Ghi số liệu thật vào một module như `nha_pho_mau.py`.
- Số liệu ghi bằng **mm**, gốc tọa độ tại giao trục A-1 (góc trước bên trái), trục x dọc mặt
  tiền, trục y vào sâu. Tường ghi theo **trục tường**.
- Trong script, đổi sang feet bằng `vn_don_vi`: `ft(3600)`, `diem(x, y)`, `chu_nhat(...)`.
  Hàm của pyrevitlib cũng nhận chuỗi có đơn vị như `"3600mm"`.
- Chạy `kiem_tra()` của module dữ liệu trước mỗi chặng. Còn lỗi thì sửa dữ liệu hoặc hỏi
  người dùng, không dựng.
- Truyền thư mục này làm `workspace` cho `run_query`, `run_modify`, rồi `import nha_pho_mau`.

## 3. Quy ước Việt Nam

| Mục | Quy ước |
|---|---|
| Đơn vị | Dữ liệu mm; diện tích m², thể tích m³ khi báo lại |
| Cao độ | ±0.000 tại mặt sàn hoàn thiện tầng 1; tên tầng theo bản vẽ, ví dụ "Tầng 1", "Tầng 2", "Mái" |
| Tường | Đặt theo trục; tường bao 200, tường ngăn 100 nếu bản vẽ không ghi khác; cao từ tầng này tới tầng trên (`top_level`) |
| Cửa | Ký hiệu D1, D2 cho cửa đi, S1, S2 cho cửa sổ, ghi vào tham số Mark |
| Phòng | Số phòng 101, 102 cho tầng 1; 201 cho tầng 2; tên theo bản vẽ |
| Kết cấu | Cột, dầm cần family kết cấu đã nạp. Vật liệu theo bản vẽ; bản vẽ không ghi thì hỏi người dùng, không tự gán mác bê tông |
| Đánh dấu | Mọi phần tử chặng tạo ra mang Comments `vn:<chặng>`, ví dụ `vn:tuong-t1` |

Tên tầng, tên phòng có dấu tiếng Việt: trên IronPython 2.7 dùng chuỗi unicode (`u"Tầng 1"`)
và dòng khai báo `# -*- coding: utf-8 -*-` đầu script.

## 4. Dựng theo chặng

Mỗi chặng một `run_modify`. Trước mỗi chặng:

1. Nói với người dùng chặng này tạo gì, bao nhiêu phần tử.
2. Chạy `run_modify` với `dry_run=true`, báo lại số phần tử thêm, cảnh báo (`failures`).
3. Chạy `run_modify` thật. Revit hiện hộp **Keep / Discard**: nói người dùng xem phần tử được
   tô sáng rồi bấm. Bấm Discard thì hỏi cần sửa gì, không chạy lại y nguyên.
4. Sau chặng: `capture_view(view="3d")` hoặc mặt bằng, đọc lại một con số (số tường, chiều
   cao, diện tích) so với dữ liệu.

Thứ tự:

| # | Chặng | Ghi chú |
|---|---|---|
| 1 | Tầng (Level) | Tạo hoặc đổi tên tầng có sẵn cho khớp bản vẽ; không xóa tầng có view đang dùng khi chưa hỏi |
| 2 | Tường từng tầng | Điểm đầu, cuối các tường gặp nhau phải trùng nhau để Revit tự nối |
| 3 | Phòng | Đặt ngay sau tường: `create_room` báo lỗi là tường còn hở |
| 4 | Sàn | Viền kín, theo tầng |
| 5 | Cửa đi, cửa sổ | Cách đầu tường, chỗ giao tường ít nhất nửa bề rộng cửa cộng 152 mm |
| 6 | Cột, dầm, mái, cầu thang | Theo skill `modeling`; cầu thang tính số bậc theo chiều cao tầng |

Mỗi chặng chạy lại được: đầu script xóa phần tử có đúng nhãn Comments của chặng đó rồi mới
tạo lại, để không bị trùng.

Mẫu chặng tường:

```python
# -*- coding: utf-8 -*-
from pyrevit import revit
from pyrevit.revit.db import query, create, delete
import nha_pho_mau as plan
import vn_don_vi as u

loi = plan.kiem_tra()
if loi:
    raise Exception("Du lieu mat bang con loi: " + "; ".join(loi))

LOAI_TUONG = inputs["loai_tuong"]  # {"200": "<ten loai trong mo hinh>", "100": "..."}
tao = 0
with revit.Transaction("vn: tuong"):
    for w in plan.TUONG:
        nhan = plan.NHAN + "tuong-" + w["ten"]
        cu = query.get_elements_by_parameter("Comments", nhan)
        if cu:
            delete.delete_elements(cu)
        wall = create.create_wall(u.diem(*w["tu"]), u.diem(*w["den"]), LOAI_TUONG[str(w["day"])],
                                  level=w["tang"], top_level=w["den_tang"])
        wall.get_Parameter(DB.BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS).Set(nhan)
        tao += 1
result = {"tuong": tao}
```

Tên hàm, tham số trong mẫu lấy theo pyrevitlib 7.0. Gặp `AttributeError` hay `TypeError` thì tra
`lookup_revit_api` hoặc `lookup_pyrevit_api`, không đoán.

## 5. Kiểm lại bằng vn-revit-mcp

Dựng xong, gọi các công cụ của vn-revit-mcp để đối chiếu với dữ liệu:

- `khoi_luong_tuong`: tổng chiều dài từng loại tường theo tầng.
- `thong_ke_cua`: số cửa đi, cửa sổ theo kích thước; cửa thiếu Mark.
- `thong_ke_phong`: diện tích phòng, phòng chưa khép kín.

Lệch so với dữ liệu thì báo con số hai bên, không tự sửa.

## 6. Trước khi báo xong

- [ ] Mọi kích thước có nguồn: tờ bản vẽ, file, hoặc lời người dùng (ghi ngày).
- [ ] `kiem_tra()` không còn lỗi.
- [ ] Mỗi chặng đã chạy thử rồi mới chạy thật; người dùng đã bấm Keep.
- [ ] Đếm theo nhãn `vn:` không có phần tử trùng.
- [ ] Phòng đều đặt được, diện tích khớp bản vẽ.
- [ ] Đã xem ảnh 3D và mặt bằng.
- [ ] Đã liệt kê chỗ còn `[Chờ bổ sung]` và giả định đã dùng (loại tường, family thay thế).

Báo cho người dùng: đây là mô hình dựng theo dữ liệu, phải được kiến trúc sư, kỹ sư kiểm tra
trước khi dùng cho hồ sơ xin phép hay thi công.
