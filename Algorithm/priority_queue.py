# =============================================================================
# Algorithm/priority_queue.py
# Hàng đợi ưu tiên bệnh nhân — xây dựng trên ADT MinHeap.
#
# Đây là tầng GIẢI THUẬT: biết về "bệnh nhân", dùng MinHeap để sắp xếp
# theo mức độ ưu tiên, đồng thời tích hợp logic ID tự động.
#
# Tại sao tách khỏi MinHeap?
#   MinHeap là cấu trúc dữ liệu chung (không biết Patient là gì).
#   PriorityQueue là lớp ứng dụng: biết Patient, biết patient_id,
#   biết cách sinh ID tự động, biết cách ghi/đọc CSV.
#
# Độ phức tạp (kế thừa từ MinHeap):
#   enqueue      : O(log N)
#   dequeue      : O(log N)
#   peek         : O(1)
#   contains     : O(N)
#   remove_by_id : O(N)
#   reinsert     : O(N)  — xóa + chèn lại khi sửa priority
# =============================================================================

import csv
import os
import sys

from DataStructures.min_heap import MinHeap
from Data.patient import Patient, SEVERITY_LABELS, QUEUE_CSV_FIELDS

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'Data', 'dataset')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

QUEUE_FILE = os.path.join(DATA_DIR, 'queue.csv')


class PriorityQueue:
    """
    Hàng đợi ưu tiên bệnh nhân dùng MinHeap.

    Ngoài heap, lớp này quản lý:
        _id_counter (int): Bộ đếm ID toàn hệ thống — tự động sinh BN0001, BN0002, ...
                           Format {:04d} đảm bảo ID luôn đủ 4 chữ số (BN0001 → BN9999).
                           Từ BN10000 trở đi tự nhiên dài hơn — không bao giờ bị trùng.
        _reg_counter(int): Bộ đếm thứ tự đăng ký — tie-breaker khi trùng sev+arrival.

    Cả hai counter được lưu vào file để không reset khi khởi động lại.
    """

    ID_PREFIX     = "BN"
    # Sửa lại dòng này để trỏ vào thư mục data_files vừa tạo ở trên
    COUNTER_FILE  = os.path.join(os.path.dirname(__file__), '..', 'Data', 'dataset', 'counters.txt')

    def __init__(self):
        self._heap         = MinHeap()
        self._id_counter   = 0
        self._reg_counter  = 0
        self._load_counters()

    # ─── SINH ID TỰ ĐỘNG ──────────────────────────────────────────────────────

    def next_patient_id(self) -> str:
        """
        Sinh mã bệnh nhân tiếp theo dạng BNxxxx (4 chữ số, có padding).

        Ví dụ: BN0001, BN0002, ..., BN0099, BN0100, ..., BN9999, BN10000, ...
        Số thứ tự tăng dần, KHÔNG bao giờ reset dù khởi động lại.

        Trả về: str — mã mới (counter đã được tăng và lưu file)
        """
        self._id_counter += 1
        self._save_counters()
        return f"{self.ID_PREFIX}{self._id_counter:04d}"

    def _next_reg_order(self) -> int:
        """Sinh số thứ tự đăng ký tiếp theo (nội bộ). Tăng và lưu ngay."""
        self._reg_counter += 1
        self._save_counters()
        return self._reg_counter

    # ─── THAO TÁC CHÍNH ───────────────────────────────────────────────────────

    def enqueue(self, patient: Patient) -> None:
        """
        Thêm bệnh nhân vào hàng đợi.

        Nếu patient.reg_order == 0 (bệnh nhân mới chưa có thứ tự đăng ký)
        → tự động gán reg_order.

        Độ phức tạp: O(log N)
        """
        if patient.reg_order == 0:
            patient.reg_order = self._next_reg_order()
        self._heap.insert(patient)

    def dequeue(self) -> Patient | None:
        """
        Lấy bệnh nhân ưu tiên nhất ra khỏi hàng đợi.
        Độ phức tạp: O(log N)

        Trả về: Patient hoặc None nếu rỗng.
        """
        return self._heap.extract_min()

    def peek(self) -> Patient | None:
        """
        Xem bệnh nhân ưu tiên nhất mà KHÔNG lấy ra.
        Độ phức tạp: O(1)
        """
        return self._heap.peek_min()

    def contains(self, patient_id: str) -> bool:
        """Kiểm tra bệnh nhân có trong hàng đợi không. O(N)"""
        return self._heap.find(lambda p: p.patient_id == patient_id) is not None

    def remove_by_id(self, patient_id: str) -> Patient | None:
        """
        Xóa bệnh nhân theo ID khỏi hàng đợi.
        Độ phức tạp: O(N)

        Trả về: Patient đã xóa, hoặc None nếu không tìm thấy.
        """
        return self._heap.delete(lambda p: p.patient_id == patient_id)

    def reinsert(self, patient: Patient) -> None:
        """
        Xóa bệnh nhân khỏi heap rồi chèn lại — dùng khi severity thay đổi.

        Tại sao cần method riêng?
            Vị trí trong heap phụ thuộc vào severity. Khi severity thay đổi,
            phần tử cũ nằm sai vị trí → phải xóa và chèn lại để heap hợp lệ.
            reg_order GIỮ NGUYÊN: bệnh nhân không mất thứ tự tie-break ban đầu.

        Độ phức tạp: O(N) — do remove_by_id là O(N).
        """
        self._heap.delete(lambda p: p.patient_id == patient.patient_id)
        self._heap.insert(patient)

    def get_sorted_list(self) -> list:
        """
        Trả về list bệnh nhân đã sắp xếp theo thứ tự ưu tiên.
        KHÔNG thay đổi heap gốc.
        Độ phức tạp: O(N log N)
        """
        return self._heap.to_sorted_list()

    def is_empty(self) -> bool:
        return self._heap.is_empty()

    def size(self) -> int:
        return self._heap.size()

    def clear(self) -> None:
        self._heap.clear()

    def get_all(self) -> list:
        """Trả về tham chiếu mảng nội bộ (chỉ đọc)."""
        return self._heap.get_raw()

    # ─── LƯU / ĐỌC FILE ──────────────────────────────────────────────────────

    def save_to_file(self, filepath=None) -> None:
        """Ghi toàn bộ hàng đợi ra file CSV. O(N)"""
        filepath = filepath or QUEUE_FILE
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=QUEUE_CSV_FIELDS)
                writer.writeheader()
                for p in self._heap.get_raw():
                    writer.writerow(p.to_dict())
        except IOError as e:
            print(f"[PriorityQueue] Lỗi ghi file: {e}")

    def load_from_file(self, filepath=None) -> None:
        """
        Đọc hàng đợi từ file CSV.
        Độ phức tạp: O(N log N)
        """
        filepath = filepath or QUEUE_FILE
        self._heap.clear()
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    p = Patient.from_dict(row)
                    self._heap.insert(p)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[PriorityQueue] Lỗi đọc file: {e}")

    def _save_counters(self) -> None:
        """Lưu id_counter và reg_counter xuống file để không mất khi tắt."""
        try:
            os.makedirs(os.path.dirname(self.COUNTER_FILE), exist_ok=True)
            with open(self.COUNTER_FILE, 'w') as f:
                f.write(f"{self._id_counter}\n{self._reg_counter}\n")
        except IOError:
            pass

    def _load_counters(self) -> None:
        """Đọc lại counter từ file khi khởi động."""
        try:
            with open(self.COUNTER_FILE, 'r') as f:
                lines = f.readlines()
                self._id_counter  = int(lines[0].strip())
                self._reg_counter = int(lines[1].strip())
        except (FileNotFoundError, IndexError, ValueError):
            self._id_counter  = 0
            self._reg_counter = 0

    # ─── HIỂN THỊ ─────────────────────────────────────────────────────────────

    def display(self) -> None:
        """In danh sách bệnh nhân theo thứ tự ưu tiên."""
        if self.is_empty():
            print("  Hàng đợi rỗng.")
            return

        sorted_list = self.get_sorted_list()
        W = 80
        print(f"\n{'─' * W}")
        print(f"  DANH SÁCH BỆNH NHÂN ĐANG CHỜ ({self.size()} người)")
        print(f"{'─' * W}")
        print(f"  {'STT':<5} {'Mã BN':<9} {'Tên':<22} {'Tuổi':<6} "
              f"{'Mức độ':<16} {'Giờ đến':<8} {'Đăng ký #'}")
        print(f"{'─' * W}")
        for i, p in enumerate(sorted_list, 1):
            label = SEVERITY_LABELS.get(p.severity, str(p.severity))
            print(f"  {i:<5} {p.patient_id:<9} {p.name:<22} {p.age:<6} "
                  f"{p.severity}-{label:<14} {p.arrival_time:<8} {p.reg_order}")
        print(f"{'─' * W}")

    def get_display_rows(self) -> list:
        """Trả về list tuple cho Treeview Tkinter."""
        rows = []
        for i, p in enumerate(self.get_sorted_list(), 1):
            label = SEVERITY_LABELS.get(p.severity, str(p.severity))
            rows.append((i, p.patient_id, p.name, p.age,
                         f"{p.severity} - {label}", p.arrival_time))
        return rows


# =============================================================================
# KIỂM TRA THỦ CÔNG
# =============================================================================
if __name__ == "__main__":
    PriorityQueue.COUNTER_FILE = '/tmp/test_counters.txt'

    print("=== Test PriorityQueue ===\n")

    pq = PriorityQueue()
    pq._id_counter  = 0
    pq._reg_counter = 0
    pq._save_counters()

    print("TEST 1 — Sinh ID tự động (4 chữ số):")
    ids = [pq.next_patient_id() for _ in range(5)]
    print(f"  IDs: {ids}")
    print(f"  Kỳ vọng: ['BN0001', 'BN0002', 'BN0003', 'BN0004', 'BN0005']")

    print("\nTEST 2 — Enqueue và thứ tự ưu tiên:")
    pq2 = PriorityQueue()
    pq2._id_counter  = 5
    pq2._reg_counter = 5
    pq2._save_counters()

    patients = [
        Patient("BN0006", "Nguyen A",  45, 1, "08:00"),
        Patient("BN0007", "Tran B",    30, 1, "08:00"),
        Patient("BN0008", "Le C",      60, 2, "07:00"),
        Patient("BN0009", "Pham D",    25, 1, "07:30"),
    ]
    for p in patients:
        pq2.enqueue(p)

    print("  Thứ tự gọi khám:")
    print("  Kỳ vọng: BN0006 → BN0007 (cùng sev=1,08:00, reg nhỏ hơn) → BN0009 → BN0008")
    while not pq2.is_empty():
        p = pq2.dequeue()
        print(f"    {p.patient_id} sev={p.severity} arr={p.arrival_time} reg={p.reg_order}")

    print("\nTEST 3 — reinsert sau khi sửa severity:")
    pq3 = PriorityQueue()
    pq3._id_counter  = 9
    pq3._reg_counter = 9
    pq3._save_counters()
    for name, sev, arr in [("X", 3, "08:00"), ("Y", 1, "09:00"), ("Z", 5, "07:00")]:
        pid = pq3.next_patient_id()
        pq3.enqueue(Patient(pid, name, 30, sev, arr))

    # Tìm X (sev=3), sửa thành sev=1, reinsert → X phải được gọi trước Y
    all_pts = pq3.get_all()
    x = next(p for p in all_pts if p.name == "X")
    x.severity = 1
    pq3.reinsert(x)
    print(f"  Sau khi sửa X từ sev=3 → sev=1:")
    print(f"  Kỳ vọng: X (reg nhỏ hơn Y vì đăng ký trước) → Y → Z")
    while not pq3.is_empty():
        p = pq3.dequeue()
        print(f"    {p.patient_id} ({p.name}) sev={p.severity} reg={p.reg_order}")

    print("\n✓ Tất cả test PriorityQueue hoàn thành.")
