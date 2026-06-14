# =============================================================================
# Algorithm/history.py
# Theo dõi lịch sử bệnh nhân đã khám — xây dựng trên ADT LinkedList.
#
# Đây là tầng GIẢI THUẬT: biết về "bệnh nhân", dùng LinkedList để
# lưu trữ theo thứ tự thời gian, hỗ trợ tìm kiếm theo ID và tên.
#
# Độ phức tạp:
#   add_record           : O(1)  — append vào cuối LinkedList
#   search_by_id         : O(N)  — duyệt toàn bộ
#   search_by_name       : O(N)
#   get_latest           : O(N)
#   save/load            : O(N)
# =============================================================================

import csv
import os
import sys

from DataStructures.linked_list import LinkedList
from Data.patient import Patient, SEVERITY_LABELS

HISTORY_FILE   = os.path.join(os.path.dirname(__file__), '..', 'Data', 'dataset', 'history.csv')
HISTORY_FIELDS = ['PatientID', 'Name', 'Age', 'SeverityScore',
                  'ArrivalTime', 'RegOrder', 'TimeCalled']


class HistoryRecord:
    """
    Một bản ghi lịch sử: bệnh nhân + giờ được gọi vào khám.

    Đây là kiểu dữ liệu của mỗi nút trong LinkedList lịch sử.
    """

    def __init__(self, patient, time_called):
        self.patient     = patient
        self.time_called = time_called   # "HH:MM:SS"

    def __repr__(self):
        return f"HistoryRecord({self.patient.patient_id}, called={self.time_called})"


class History:
    """
    Lưu trữ lịch sử bệnh nhân đã khám theo thứ tự thời gian.
    Dùng LinkedList để thêm O(1) và duyệt tuần tự O(N).
    """

    def __init__(self):
        self._list = LinkedList()   # LinkedList[HistoryRecord]

    # ─── THAO TÁC CHÍNH ───────────────────────────────────────────────────────

    def add_record(self, patient, time_called):
        """
        Thêm một lượt khám vào cuối lịch sử.
        Độ phức tạp: O(1)
        """
        record = HistoryRecord(patient, time_called)
        self._list.append(record)

    def search_by_id(self, patient_id):
        """
        Tìm tất cả lượt khám của bệnh nhân theo mã.
        Một bệnh nhân có thể tái khám nhiều lần.
        Độ phức tạp: O(N)

        Trả về: list[HistoryRecord]
        """
        return self._list.find_all(
            lambda r: r.patient.patient_id == patient_id
        )

    def search_by_name(self, name):
        """
        Tìm lịch sử theo tên bệnh nhân (gần đúng, không phân biệt hoa thường).
        Độ phức tạp: O(N)

        Trả về: list[HistoryRecord]
        """
        name_lower = name.lower()
        return self._list.find_all(
            lambda r: name_lower in r.patient.name.lower()
        )

    def get_total(self):
        """Tổng số lượt đã khám. O(1)"""
        return self._list.size()

    def get_latest(self, n=5):
        """
        Lấy N lượt khám gần nhất.
        Độ phức tạp: O(N)

        Trả về: list[HistoryRecord]
        """
        return self._list.get_last_n(n)

    def get_all(self):
        """Trả về toàn bộ lịch sử dưới dạng list. O(N)"""
        return self._list.to_list()

    def clear(self):
        """Xóa toàn bộ lịch sử."""
        self._list.clear()

    # ─── LƯU / ĐỌC FILE ──────────────────────────────────────────────────────

    def save_to_file(self, filepath=None):
        """Ghi toàn bộ lịch sử ra file CSV. O(N)"""
        filepath = filepath or HISTORY_FILE
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
                writer.writeheader()
                for record in self._list.to_list():
                    p = record.patient
                    writer.writerow({
                        'PatientID'    : p.patient_id,
                        'Name'         : p.name,
                        'Age'          : p.age,
                        'SeverityScore': p.severity,
                        'ArrivalTime'  : p.arrival_time,
                        'RegOrder'     : p.reg_order,
                        'TimeCalled'   : record.time_called
                    })
        except IOError as e:
            print(f"[History] Lỗi ghi file: {e}")

    def load_from_file(self, filepath=None):
        """Đọc lịch sử từ file CSV. O(N)"""
        filepath = filepath or HISTORY_FILE
        self.clear()
        try:
            with open(filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    p = Patient.from_dict(row)
                    self.add_record(p, row['TimeCalled'])
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"[History] Lỗi đọc file: {e}")

    # ─── HIỂN THỊ ─────────────────────────────────────────────────────────────

    def display_all(self):
        """In toàn bộ lịch sử dạng bảng."""
        records = self._list.to_list()
        if not records:
            print("  Chưa có bệnh nhân nào được khám.")
            return

        W = 82
        print(f"\n{'─' * W}")
        print(f"  LỊCH SỬ BỆNH NHÂN ĐÃ KHÁM ({self.get_total()} lượt)")
        print(f"{'─' * W}")
        print(f"  {'STT':<5} {'Mã BN':<8} {'Tên':<22} {'Tuổi':<6} "
              f"{'Mức độ':<16} {'Giờ đến':<10} {'Giờ khám'}")
        print(f"{'─' * W}")
        for i, record in enumerate(records, 1):
            p     = record.patient
            label = SEVERITY_LABELS.get(p.severity, str(p.severity))
            print(f"  {i:<5} {p.patient_id:<8} {p.name:<22} {p.age:<6} "
                  f"{p.severity}-{label:<14} {p.arrival_time:<10} "
                  f"{record.time_called}")
        print(f"{'─' * W}")
        print(f"  Tổng: {self.get_total()} lượt")

    def get_display_rows(self):
        """Trả về list tuple cho Treeview Tkinter."""
        rows = []
        for i, record in enumerate(self._list.to_list(), 1):
            p     = record.patient
            label = SEVERITY_LABELS.get(p.severity, str(p.severity))
            rows.append((i, p.patient_id, p.name, p.age,
                         f"{p.severity} - {label}",
                         p.arrival_time, record.time_called))
        return rows


# =============================================================================
# KIỂM TRA THỦ CÔNG
# =============================================================================
if __name__ == "__main__":
    print("=== Test History ===\n")

    ht = History()

    data = [
        ("BN002", "Tran Thi Binh",  30, 1, "08:30", 2, "08:35:12"),
        ("BN001", "Nguyen Van An",   45, 3, "08:00", 1, "08:36:05"),
        ("BN003", "Le Van Cuong",    60, 2, "07:00", 3, "08:45:30"),
    ]

    print("TEST 1 — Thêm lịch sử:")
    for pid, name, age, sev, arr, reg, called in data:
        p = Patient(pid, name, age, sev, arr, reg_order=reg)
        ht.add_record(p, called)
    print(f"  Tổng: {ht.get_total()} → Kỳ vọng: 3")

    print("\nTEST 2 — Hiển thị:")
    ht.display_all()

    print("\nTEST 3 — Tìm theo ID:")
    results = ht.search_by_id("BN001")
    print(f"  Tìm BN001: {len(results)} kết quả → Kỳ vọng: 1")

    print("\nTEST 4 — get_latest(2):")
    latest = ht.get_latest(2)
    print(f"  2 gần nhất: {[r.patient.patient_id for r in latest]}")
    print(f"  Kỳ vọng: ['BN001', 'BN003']")

    print("\n✓ Tất cả test History hoàn thành.")
