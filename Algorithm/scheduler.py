# =============================================================================
# Algorithm/scheduler.py
# Điều phối toàn bộ nghiệp vụ quản lý bệnh nhân.
#
# Đây là tầng GIẢI THUẬT cao nhất: kết hợp ba cấu trúc dữ liệu:
#   PriorityQueue  → xác định ai khám tiếp (Min-Heap)
#   HashMap        → tra cứu O(1) theo patient_id
#   History → lưu lịch sử theo thứ tự thời gian (LinkedList)
#
# Đây là lớp duy nhất mà UI cần giao tiếp.
# Patient ID và reg_order được sinh hoàn toàn tự động tại đây.
#
# Quy tắc encapsulation:
#   Scheduler KHÔNG truy cập trực tiếp vào _heap của PriorityQueue.
#   Mọi thao tác heap đi qua các method public của PriorityQueue
#   (enqueue, dequeue, reinsert, remove_by_id, ...).
#   Điều này đảm bảo PriorityQueue có thể thay đổi nội bộ mà không
#   ảnh hưởng đến Scheduler.
# =============================================================================

import os
import sys
from datetime import datetime

from DataStructures.hash_map    import HashMap
from Algorithm.priority_queue   import PriorityQueue
from Algorithm.history  import History
from Data.patient               import Patient, SEVERITY_LABELS, validate_arrival_time


class Scheduler:
    """
    Bộ điều phối hàng đợi bệnh viện.

    Thuộc tính:
        _queue    (PriorityQueue) : Hàng đợi chờ khám — xác định thứ tự
        _registry (HashMap)       : Tra cứu O(1) theo patient_id
        _history  (History): Lịch sử đã khám theo thứ tự thời gian

    Tại sao cần cả _queue lẫn _registry?
        _queue    → biết AI được gọi tiếp theo (theo priority)
        _registry → kiểm tra ID trùng, tìm theo ID trong O(1)
        Cả hai cùng lưu tập bệnh nhân đang chờ, nhưng phục vụ mục đích khác nhau.

    Nguyên tắc nhất quán dữ liệu:
        Mọi thao tác thêm/xóa/sửa phải cập nhật CẢ HAI _queue VÀ _registry.
        Nếu chỉ cập nhật một bên → dữ liệu mất đồng bộ → lỗi khó tìm.
    """

    def __init__(self):
        self._queue    = PriorityQueue()
        self._registry = HashMap()
        self._history  = History()

    # ─── LOAD / SAVE ──────────────────────────────────────────────────────────

    def loadData(self) -> None:
        """Tải hàng đợi và lịch sử từ file khi khởi động."""
        self._queue.load_from_file()
        self._registry.clear()
        for p in self._queue.get_all():
            self._registry.put(p.patient_id, p)

        self._history.load_from_file()
        print(f"[Scheduler] Sẵn sàng. "
              f"Đang chờ: {self._queue.size()} | "
              f"Đã khám: {self._history.get_total()}")

    def saveData(self) -> None:
        """Lưu hàng đợi và lịch sử xuống file."""
        self._queue.save_to_file()
        self._history.save_to_file()

    # ─── THÊM BỆNH NHÂN ───────────────────────────────────────────────────────

    def add_patient(self, name, age, severity,
                    arrival_time=None) -> tuple[bool, str, Patient | None]:
        """
        Thêm bệnh nhân mới vào hàng đợi.

        PatientID và reg_order được sinh TỰ ĐỘNG — người dùng không nhập.

        Tham số:
            name         (str): Họ và tên
            age          (int): Tuổi
            severity     (int): Mức độ bệnh 1–5
            arrival_time (str): Giờ đến "HH:MM", mặc định = giờ hiện tại

        Trả về: (bool, str, Patient | None) — (thành công, thông báo, bệnh nhân)
        """
        ok, err = self._validate(name, age, severity)
        if not ok:
            return False, err, None

        # Xử lý và validate arrival_time
        if arrival_time is None or str(arrival_time).strip() == "":
            arrival_time = datetime.now().strftime("%H:%M")
        else:
            ok_t, result = validate_arrival_time(arrival_time)
            if not ok_t:
                return False, result, None
            arrival_time = result   # đã chuẩn hoá format HH:MM

        patient_id = self._queue.next_patient_id()
        p = Patient(patient_id, str(name).strip(), int(age),
                    int(severity), arrival_time, reg_order=0)

        self._queue.enqueue(p)           # gán reg_order tại đây
        self._registry.put(patient_id, p)
        self.saveData()

        label = SEVERITY_LABELS.get(int(severity), str(severity))
        msg   = (f"Đã thêm {p.name} | Mã: {patient_id} | "
                 f"Mức: {label} | Giờ đến: {arrival_time}")
        return True, msg, p

    # ─── GỌI KHÁM ─────────────────────────────────────────────────────────────

    def call_next(self) -> Patient | None:
        """
        Gọi bệnh nhân ưu tiên nhất vào khám.

        Quy trình:
            1. dequeue khỏi PriorityQueue
            2. Xóa khỏi HashMap registry
            3. Ghi vào History với giờ hiện tại
            4. Lưu file

        Trả về: Patient vừa được gọi, hoặc None nếu hàng đợi rỗng.
        """
        if self._queue.is_empty():
            return None

        p           = self._queue.dequeue()
        time_called = datetime.now().strftime("%H:%M:%S")

        self._registry.delete(p.patient_id)
        self._history.add_record(p, time_called)
        self.saveData()

        return p

    # ─── XÓA ──────────────────────────────────────────────────────────────────

    def remove_patient(self, patient_id: str) -> tuple[bool, str]:
        """
        Xóa bệnh nhân khỏi hàng đợi (ví dụ: bệnh nhân tự rời đi).

        Trả về: (bool, str)
        """
        patient_id = str(patient_id).strip()

        if not self._registry.has(patient_id):
            return False, f"Không tìm thấy '{patient_id}' trong hàng đợi."

        removed = self._queue.remove_by_id(patient_id)
        if removed is None:
            return False, "Xóa thất bại (lỗi nội bộ)."

        self._registry.delete(patient_id)
        self.saveData()
        return True, f"Đã xóa {removed.name} ({patient_id}) khỏi hàng đợi."

    # ─── SỬA ──────────────────────────────────────────────────────────────────

    def edit_patient(self, patient_id, new_name=None,
                     new_age=None, new_severity=None) -> tuple[bool, str]:
        """
        Cập nhật thông tin bệnh nhân đang chờ.

        Khi sửa severity → dùng PriorityQueue.reinsert() để di chuyển
        bệnh nhân đến đúng vị trí trong heap mà không vi phạm encapsulation.
        reg_order GIỮ NGUYÊN để thứ tự tie-break không thay đổi.

        Khi chỉ sửa name/age → không cần reinsert vì vị trí heap không đổi
        (heap sắp xếp theo severity, arrival_time, reg_order — không phải name/age).

        Trả về: (bool, str)
        """
        patient_id = str(patient_id).strip()

        if not self._registry.has(patient_id):
            return False, f"Không tìm thấy '{patient_id}' trong hàng đợi."

        p = self._registry.get(patient_id)

        if new_severity is not None:
            try:
                sev = int(new_severity)
                if not (1 <= sev <= 5):
                    return False, "Mức độ bệnh phải từ 1 đến 5."
            except (ValueError, TypeError):
                return False, "Mức độ bệnh không hợp lệ."

            p.severity = sev
            # reinsert() thay thế truy cập trực tiếp _heap — đúng encapsulation
            self._queue.reinsert(p)

        if new_name is not None and str(new_name).strip():
            p.name = str(new_name).strip()

        if new_age is not None:
            try:
                age = int(new_age)
                if not (1 <= age <= 150):
                    return False, "Tuổi phải từ 1 đến 150."
                p.age = age
            except (ValueError, TypeError):
                return False, "Tuổi phải là số nguyên."

        self.saveData()
        return True, f"Đã cập nhật thông tin bệnh nhân {p.name} ({patient_id})."

    # ─── TÌM KIẾM ─────────────────────────────────────────────────────────────

    def search_by_id(self, patient_id: str) -> Patient | None:
        """
        Tìm bệnh nhân đang chờ theo mã.
        O(1) nhờ HashMap.
        """
        return self._registry.get(str(patient_id).strip())

    def search_by_name(self, name: str) -> list:
        """
        Tìm bệnh nhân đang chờ theo tên (gần đúng).
        O(N) — duyệt toàn bộ queue.
        """
        name_lower = name.lower().strip()
        return [p for p in self._queue.get_all()
                if name_lower in p.name.lower()]

    def search_history_by_id(self, patient_id: str) -> list:
        """Tìm lịch sử khám theo mã bệnh nhân."""
        return self._history.search_by_id(patient_id)

    # ─── HIỂN THỊ ─────────────────────────────────────────────────────────────

    def display_queue(self) -> None:
        self._queue.display()

    def display_history(self) -> None:
        self._history.display_all()

    # ─── THỐNG KÊ ─────────────────────────────────────────────────────────────

    def count_waiting(self) -> int:
        return self._queue.size()

    def count_examined(self) -> int:
        return self._history.get_total()

    def get_next_id_preview(self) -> str:
        """
        Trả về mã bệnh nhân SẼ được sinh ở lần đăng ký tiếp theo (chỉ xem).
        KHÔNG tăng counter.
        """
        return f"{PriorityQueue.ID_PREFIX}{self._queue._id_counter + 1:04d}"

    def count_by_severity(self) -> dict:
        counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for p in self._queue.get_all():
            if p.severity in counts:
                counts[p.severity] += 1
        return counts

    def get_statistics(self) -> dict:
        return {
            'total_waiting' : self.count_waiting(),
            'total_examined': self.count_examined(),
            'by_severity'   : self.count_by_severity(),
            'next_patient'  : self._queue.peek(),
            'next_id'       : self.get_next_id_preview()
        }

    def print_statistics(self) -> None:
        stats = self.get_statistics()
        W     = 48
        print(f"\n{'═' * W}")
        print(f"  THỐNG KÊ HỆ THỐNG BỆNH VIỆN")
        print(f"{'═' * W}")
        print(f"  Mã BN tiếp theo : {stats['next_id']}")
        print(f"  Đang chờ khám   : {stats['total_waiting']:>5}")
        print(f"  Đã khám xong    : {stats['total_examined']:>5}")
        print(f"{'─' * W}")
        print(f"  Phân loại đang chờ:")
        for lvl in range(1, 6):
            count = stats['by_severity'][lvl]
            label = SEVERITY_LABELS[lvl]
            bar   = "█" * min(count, 20)
            more  = f"(+{count-20})" if count > 20 else ""
            print(f"    Mức {lvl} {label:<12}: {count:>4}  {bar}{more}")
        print(f"{'─' * W}")
        nxt = stats['next_patient']
        if nxt:
            label = SEVERITY_LABELS.get(nxt.severity, "")
            print(f"  Tiếp theo: {nxt.name} [{nxt.patient_id}] "
                  f"| Mức {nxt.severity} ({label})")
        else:
            print(f"  Tiếp theo: (không có ai)")
        print(f"{'═' * W}")

    # ─── HỖ TRỢ UI ────────────────────────────────────────────────────────────

    def get_queue_display_rows(self) -> list:
        return self._queue.get_display_rows()

    def get_history_display_rows(self) -> list:
        return self._history.get_display_rows()

    # ─── VALIDATE ─────────────────────────────────────────────────────────────

    def _validate(self, name, age, severity) -> tuple[bool, str]:
        name = str(name).strip()
        if not name:
            return False, "Tên bệnh nhân không được để trống."
        try:
            age_int = int(age)
            if not (1 <= age_int <= 150):
                return False, "Tuổi phải từ 1 đến 150."
        except (ValueError, TypeError):
            return False, "Tuổi phải là số nguyên."
        try:
            sev_int = int(severity)
            if not (1 <= sev_int <= 5):
                return False, "Mức độ bệnh phải từ 1 đến 5."
        except (ValueError, TypeError):
            return False, "Mức độ bệnh phải là số từ 1 đến 5."
        return True, ""


# =============================================================================
# KIỂM TRA THỦ CÔNG
# =============================================================================
if __name__ == "__main__":
    PriorityQueue.COUNTER_FILE = '/tmp/test_sched_counters.txt'

    print("=== Test Scheduler ===\n")

    sched = Scheduler()
    sched._queue._id_counter  = 0
    sched._queue._reg_counter = 0
    sched._queue._save_counters()

    print("TEST 1 — Thêm bệnh nhân (ID tự động 4 chữ số):")
    cases = [
        ("Nguyen Van An",  45, 3, "08:00"),
        ("Tran Thi Binh",  30, 1, "08:30"),
        ("Le Van Cuong",   60, 2, "07:00"),
        ("Pham Thi Dung",  25, 1, "08:00"),
        ("Hoang Van Em",   50, 5, "06:00"),
    ]
    for name, age, sev, arr in cases:
        ok, msg, p = sched.add_patient(name, age, sev, arr)
        print(f"  {'OK' if ok else 'FAIL'} — {msg}")

    print("\nTEST 2 — Validate arrival_time sai format:")
    ok, msg, p = sched.add_patient("Test Patient", 30, 3, "9:00")
    print(f"  '9:00' (tự-fix) → {'OK' if ok else 'FAIL'}: {msg}")
    ok, msg, p = sched.add_patient("Test Patient", 30, 3, "25:00")
    print(f"  '25:00' (lỗi)   → {'OK' if ok else 'FAIL'}: {msg}")

    print("\nTEST 3 — Xem hàng đợi:")
    sched.display_queue()

    print("\nTEST 4 — Gọi khám (tie-break):")
    print("  Kỳ vọng: BN0002 (sev=1,08:30,reg=2) trước BN0004 (sev=1,08:00?) — ủa")
    print("  Thực ra: BN0004 arr=08:00 < BN0002 arr=08:30 → BN0004 trước")
    for _ in range(3):
        p = sched.call_next()
        print(f"  → {p.patient_id} {p.name} (sev={p.severity}, "
              f"arr={p.arrival_time}, reg={p.reg_order})")

    print("\nTEST 5 — Sửa severity, dùng reinsert (không vi phạm encapsulation):")
    remaining = sched._queue.get_all()
    if remaining:
        target = remaining[0]
        old_sev = target.severity
        ok, msg = sched.edit_patient(target.patient_id, new_severity=1)
        print(f"  Sửa {target.patient_id} sev={old_sev}→1: {msg}")
        sched.display_queue()

    print("\nTEST 6 — Thống kê:")
    sched.print_statistics()

    print("\n✓ Tất cả test Scheduler hoàn thành.")
