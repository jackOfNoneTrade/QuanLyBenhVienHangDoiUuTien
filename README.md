# Hệ thống Quản lý Hàng đợi Bệnh viện

**Đề tài:** Hệ thống quản lý bệnh viện sử dụng hàng đợi ưu tiên  
**Môn:** Cấu trúc dữ liệu và Giải thuật — ĐH Bách Khoa Hà Nội  
**Nhóm:** 9 | **GVHD:** Vương Mai Phương

**LINK REPO GITHUB** : [https://github.com/jackOfNoneTrade/QuanLyBenhVienHangDoiUuTien]
**LINK VIDEO THUYẾT TRÌNH**: [https://youtu.be/r3ubgxttJWk?si=B_zyl-o_fQiXZR_W]

---

## Yêu cầu hệ thống

- **Python ≥ 3.10** (dùng `X | Y` type hint)
- Không cần cài thêm thư viện ngoài (chỉ dùng thư viện chuẩn)

Kiểm tra phiên bản Python:
```bash
python --version
```

---

## Cách chạy chương trình

```bash
# Di chuyển vào thư mục dự án
cd HospitalQueue

# Chạy chương trình chính
python main.py
```

Lần đầu chạy, thư mục `Data/dataset/` sẽ tự động được tạo để lưu dữ liệu.

---

## Tạo dữ liệu mẫu (tùy chọn)

Muốn có sẵn bệnh nhân khi mở chương trình lần đầu, chạy script tạo dataset mẫu trước:

```bash
# Tạo mặc định: 15 bệnh nhân đang chờ + 8 lịch sử
python generate_dataset.py

# Tùy chỉnh số lượng
python generate_dataset.py --queue 30 --history 15

# Xóa dataset cũ và tạo lại từ đầu
python generate_dataset.py --reset

# Đổi hạt giống random (để có bộ dữ liệu khác)
python generate_dataset.py --seed 123 --queue 20 --history 10
```

| Tùy chọn | Mô tả | Mặc định |
|---|---|---|
| `--queue N` | Số bệnh nhân trong hàng đợi | 15 |
| `--history N` | Số bản ghi lịch sử đã khám | 8 |
| `--seed N` | Hạt giống random (kết quả tái lặp được) | 42 |
| `--reset` | Xóa dataset cũ trước khi tạo mới | — |

---

## Chạy kiểm thử tự động (26 test case)

```bash
cd HospitalQueue

# Cách 1 — chạy trực tiếp (khuyên dùng)
python tests/test_all.py

# Cách 2 — dùng pytest (nếu đã cài)
pip install pytest
python -m pytest tests/test_all.py -v
```

Kết quả mong đợi:
```
KẾT QUẢ: 26/26 test case đạt  — TẤT CẢ ĐẠT ✓
```

---

## Chạy kiểm thử hiệu năng

So sánh Binary Heap với Unsorted List và Sorted List trên N = 500 → 10000 bệnh nhân:

```bash
python testperformance.py
```

Kết quả mẫu:
```
     N |  Binary Heap (ms) | Unsorted List (ms) |   Sorted List (ms)
----------------------------------------------------------------------
   500 |              0.xx |               x.xx |               x.xx
  1000 |              x.xx |               x.xx |               x.xx
  ...
```

---

## Cấu trúc dự án

```
HospitalQueue/
├── main.py                      # Điểm vào duy nhất — chạy file này
├── generate_dataset.py          # Tạo dữ liệu mẫu (bệnh nhân ngẫu nhiên)
├── testperformance.py           # So sánh hiệu năng Heap vs List
│
├── Data/
│   ├── patient.py               # Kiểu dữ liệu Patient + validate giờ đến
│   └── dataset/                 # Tự tạo khi chạy lần đầu
│       ├── queue.csv            # Hàng đợi hiện tại (tự lưu sau mỗi thao tác)
│       ├── history.csv          # Lịch sử đã khám
│       └── counters.txt         # Bộ đếm ID và reg_order (không reset)
│
├── DataStructures/
│   ├── min_heap.py              # ADT MinHeap — tự cài, KHÔNG dùng heapq
│   ├── linked_list.py           # ADT SinglyLinkedList + LinkedList (wrapper)
│   └── hash_map.py              # ADT HashMap (generic) + PatientHashMap (giáo khoa)
│
├── Algorithm/
│   ├── priority_queue.py        # PriorityQueue bệnh nhân — dùng MinHeap
│   ├── history.py               # History lưu lịch sử — dùng LinkedList
│   └── scheduler.py             # Scheduler điều phối (layer cao nhất)
│
├── UI/
│   └── main_console.py          # Giao diện dòng lệnh — chỉ gọi Scheduler
│
└── tests/
    └── test_all.py              # 26 test case tự động (TC-01 → TC-26)
```

---

## Hướng dẫn sử dụng

Sau khi chạy `python main.py`, menu hiển thị:

```
============================================================
BENH VIEN -- QUAN LY HANG DOI
Dang cho: 0 | Da kham: 0
============================================================
> [1] Them benh nhan
> [2] Goi kham (lay uu tien cao nhat)
> [3] Xem hang doi hien tai
> [4] Tim kiem benh nhan
> [5] Sua thong tin benh nhan
> [6] Xoa benh nhan khoi hang doi
> [7] Xem lich su da kham
> [8] Thong ke he thong
X [0] Thoat
```

| Chức năng | Mô tả |
|---|---|
| **[1] Thêm bệnh nhân** | Nhập tên, tuổi, mức độ (1-5), giờ đến (Enter = giờ hiện tại). Mã BN tự động sinh. |
| **[2] Gọi khám** | Hiển thị bệnh nhân ưu tiên nhất, xác nhận `y` trước khi gọi. |
| **[3] Xem hàng đợi** | Danh sách sắp xếp theo thứ tự ưu tiên. |
| **[4] Tìm kiếm** | Theo mã BN (O(1)) hoặc theo tên (O(N)). |
| **[5] Sửa thông tin** | Nhấn Enter để giữ nguyên giá trị cũ. |
| **[6] Xóa bệnh nhân** | Xác nhận `y` trước khi xóa. |
| **[7] Lịch sử** | Danh sách đã khám theo thứ tự thời gian thực tế. |
| **[8] Thống kê** | Biểu đồ ASCII theo mức độ bệnh. |

---

## Quy tắc ưu tiên 3 cấp

1. **severity** nhỏ hơn → ưu tiên hơn (1 = nguy kịch, 5 = rất nhẹ)
2. Cùng severity → **arrival_time** nhỏ hơn → ưu tiên hơn (FIFO)
3. Cùng cả hai → **reg_order** nhỏ hơn → ưu tiên hơn (tie-breaker)

---

## Lưu ý quan trọng

- **Dữ liệu tự động lưu** sau mỗi thao tác thay đổi — không mất khi tắt chương trình.
- **Mã bệnh nhân** (VD: BN0001) được sinh tự động, tăng dần, không bao giờ trùng.
- **Giờ đến** nhập theo định dạng `HH:MM` (VD: `09:30`). Định dạng `9:30` sẽ tự động được chuyển thành `09:30`.
- Để **xóa toàn bộ dữ liệu** và bắt đầu lại: xóa thư mục `Data/dataset/` hoặc chạy `python generate_dataset.py --reset`.
- **Không chạy nhiều instance** chương trình cùng lúc — có thể gây xung đột file CSV.

---

## Mô tả file kiểm thử (tests/test_all.py)

File kiểm thử tự động tương ứng với **Chương 5 — Bảng 5.1** trong báo cáo:

| Nhóm | TC | Nội dung kiểm thử |
|---|---|---|
| MinHeap | TC-01 → TC-08 | insert, extract_min, peek_min, delete, find_all, to_sorted_list |
| Patient | TC-09 → TC-16 | Quy tắc so sánh 3 cấp, __eq__, validate_arrival_time |
| PriorityQueue | TC-17 → TC-26 | reg_order, thứ tự dequeue, reinsert, save/load |
