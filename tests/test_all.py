# =============================================================================
# tests/test_all.py
# Kiểm thử tự động — 26 test case theo báo cáo (Chương 5)
#
# Chạy từ thư mục gốc HospitalQueue/:
#     python -m pytest tests/test_all.py -v
# hoặc:
#     python tests/test_all.py
#
# Nhóm test:
#   Group A — MinHeap     (TC-01 → TC-08)
#   Group B — Patient     (TC-09 → TC-16)
#   Group C — PriorityQueue + Scheduler (TC-17 → TC-26)
# =============================================================================

import sys
import os
import csv
import tempfile

# Đảm bảo Python tìm thấy các module trong thư mục gốc HospitalQueue/
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from DataStructures.min_heap    import MinHeap
from Data.patient               import Patient, validate_arrival_time
from Algorithm.priority_queue   import PriorityQueue
from Algorithm.scheduler        import Scheduler

# ─── Màu terminal (tắt nếu không hỗ trợ) ─────────────────────────────────────
_USE_COLOR = sys.stdout.isatty()
GREEN  = "\033[92m" if _USE_COLOR else ""
RED    = "\033[91m" if _USE_COLOR else ""
YELLOW = "\033[93m" if _USE_COLOR else ""
RESET  = "\033[0m"  if _USE_COLOR else ""

# ─── Hàm helper ───────────────────────────────────────────────────────────────
_results = []   # (tc_id, passed, description)

def _run(tc_id, description, func):
    """Chạy một test case, bắt mọi exception, ghi kết quả."""
    try:
        func()
        _results.append((tc_id, True, description))
        print(f"  {GREEN}✓ PASS{RESET}  [{tc_id}] {description}")
    except AssertionError as e:
        _results.append((tc_id, False, description))
        detail = str(e) if str(e) else "assertion failed"
        print(f"  {RED}✗ FAIL{RESET}  [{tc_id}] {description}")
        print(f"          → {detail}")
    except Exception as e:
        _results.append((tc_id, False, description))
        print(f"  {RED}✗ ERROR{RESET} [{tc_id}] {description}")
        print(f"          → {type(e).__name__}: {e}")


# =============================================================================
# GROUP A — MinHeap  (TC-01 → TC-08)
# =============================================================================

def tc01():
    """Insert số nguyên, extract_min trả về thứ tự tăng dần."""
    h = MinHeap()
    for x in [7, 2, 9, 1, 5, 3]:
        h.insert(x)
    result = [h.extract_min() for _ in range(6)]
    assert result == [1, 2, 3, 5, 7, 9], f"Kết quả: {result}"


def tc02():
    """Heap có đúng 1 phần tử: insert(42) → extract_min() trả về 42, heap rỗng sau đó."""
    h = MinHeap()
    h.insert(42)
    val = h.extract_min()
    assert val == 42, f"val={val}"
    assert h.is_empty(), "Heap phải rỗng sau extract_min"


def tc03():
    """peek_min() không thay đổi heap: gọi 3 lần liên tiếp, mỗi lần đều trả về 1, size vẫn 3."""
    h = MinHeap()
    for x in [5, 1, 3]:
        h.insert(x)
    for _ in range(3):
        assert h.peek_min() == 1, f"peek_min={h.peek_min()}"
    assert h.size() == 3, f"size={h.size()}"


def tc04():
    """Xóa nút lá: delete(x==9) → removed=9, còn lại [1,3,5,7]."""
    h = MinHeap()
    for x in [1, 3, 5, 7, 9]:
        h.insert(x)
    removed = h.delete(lambda x: x == 9)
    assert removed == 9, f"removed={removed}"
    assert sorted(h.get_raw()) == [1, 3, 5, 7], f"còn lại: {sorted(h.get_raw())}"


def tc05():
    """Xóa nút gốc: delete(x==1) → removed=1, còn lại [3,5,7,9]."""
    h = MinHeap()
    for x in [1, 3, 5, 7, 9]:
        h.insert(x)
    removed = h.delete(lambda x: x == 1)
    assert removed == 1, f"removed={removed}"
    assert sorted(h.get_raw()) == [3, 5, 7, 9], f"còn lại: {sorted(h.get_raw())}"


def tc06():
    """Xóa phần tử không tồn tại: delete(x==99) → None, size không đổi."""
    h = MinHeap()
    for x in [2, 4, 6]:
        h.insert(x)
    result = h.delete(lambda x: x == 99)
    assert result is None, f"result={result}"
    assert h.size() == 3, f"size={h.size()}"


def tc07():
    """find_all() tìm phần tử thỏa điều kiện: insert 1..8, find_all(x%2==0) → [2,4,6,8]."""
    h = MinHeap()
    for x in range(1, 9):
        h.insert(x)
    result = sorted(h.find_all(lambda x: x % 2 == 0))
    assert result == [2, 4, 6, 8], f"result={result}"


def tc08():
    """to_sorted_list() không phá vỡ heap: heap giữ nguyên sau khi gọi."""
    h = MinHeap()
    for x in [4, 2, 6, 1]:
        h.insert(x)
    lst = h.to_sorted_list()
    assert lst == [1, 2, 4, 6], f"sorted list={lst}"
    # Heap vẫn nguyên vẹn
    assert h.size() == 4, f"size sau={h.size()}"
    assert h.peek_min() == 1, f"peek_min={h.peek_min()}"


# =============================================================================
# GROUP B — Patient  (TC-09 → TC-16)
# =============================================================================

def tc09():
    """Severity nhỏ hơn được ưu tiên hơn: BN001(sev=1) < BN002(sev=3)."""
    p1 = Patient("BN001", "An", 30, 1, "08:00", reg_order=1)
    p2 = Patient("BN002", "Binh", 25, 3, "08:00", reg_order=2)
    assert p1 < p2, "sev=1 phải ưu tiên hơn sev=3"


def tc10():
    """Cùng severity, đến sớm hơn được ưu tiên: arr=07:30 < arr=09:00."""
    p1 = Patient("BN001", "An", 30, 2, "07:30", reg_order=1)
    p2 = Patient("BN002", "Binh", 25, 2, "09:00", reg_order=2)
    assert p1 < p2, "07:30 phải ưu tiên hơn 09:00"


def tc11():
    """Cùng sev + arr, reg_order nhỏ hơn được ưu tiên: reg=5 trước reg=10."""
    p1 = Patient("BN001", "An", 30, 2, "08:00", reg_order=5)
    p2 = Patient("BN002", "Binh", 25, 2, "08:00", reg_order=10)
    assert p1 < p2, "reg=5 phải ưu tiên hơn reg=10"


def tc12():
    """__eq__ chỉ so sánh patient_id: hai bệnh nhân cùng ID → bằng nhau."""
    p1 = Patient("BN001", "An",   30, 1, "08:00", reg_order=1)
    p2 = Patient("BN001", "Khac", 50, 5, "09:00", reg_order=99)
    assert p1 == p2, "__eq__ chỉ dựa vào patient_id"


def tc13():
    """Validate giờ đúng chuẩn HH:MM: '13:45' → (True, '13:45')."""
    ok, result = validate_arrival_time("13:45")
    assert ok is True, f"ok={ok}"
    assert result == "13:45", f"result={result}"


def tc14():
    """Chuẩn hóa H:MM thành 0H:MM: '7:05' → (True, '07:05')."""
    ok, result = validate_arrival_time("7:05")
    assert ok is True, f"ok={ok}"
    assert result == "07:05", f"result={result}"


def tc15():
    """Từ chối giờ có phút > 59: '10:61' → False."""
    ok, _ = validate_arrival_time("10:61")
    assert ok is False, "10:61 phải bị từ chối"


def tc16():
    """Từ chối chuỗi không phải giờ: 'buoi sang' → False."""
    ok, _ = validate_arrival_time("buoi sang")
    assert ok is False, "'buoi sang' phải bị từ chối"


# =============================================================================
# GROUP C — PriorityQueue + Scheduler  (TC-17 → TC-26)
# =============================================================================

def _make_pq():
    """Tạo PriorityQueue dùng counter file tạm, reset về 0."""
    PriorityQueue.COUNTER_FILE = os.path.join(
        tempfile.gettempdir(), "test_pq_counters.txt")
    pq = PriorityQueue()
    pq._id_counter  = 0
    pq._reg_counter = 0
    pq._save_counters()
    return pq


def _make_sched():
    """Tạo Scheduler dùng counter file tạm."""
    PriorityQueue.COUNTER_FILE = os.path.join(
        tempfile.gettempdir(), "test_sched_counters.txt")
    sched = Scheduler()
    sched._queue._id_counter  = 0
    sched._queue._reg_counter = 0
    sched._queue._save_counters()
    return sched


def tc17():
    """Tự gán reg_order khi enqueue: bệnh nhân mới với reg_order=0 → tự động gán ≥ 1."""
    pq = _make_pq()
    pid = pq.next_patient_id()
    p = Patient(pid, "Test", 30, 2, "08:00", reg_order=0)
    pq.enqueue(p)
    assert p.reg_order >= 1, f"reg_order={p.reg_order}"


def tc18():
    """Giữ nguyên reg_order đã có: reg_order=77 không bị ghi đè."""
    pq = _make_pq()
    pid = pq.next_patient_id()
    p = Patient(pid, "Test", 30, 2, "08:00", reg_order=77)
    pq.enqueue(p)
    assert p.reg_order == 77, f"reg_order bị ghi đè thành {p.reg_order}"


def tc19():
    """size() và is_empty() nhất quán: PriorityQueue mới → size=0, is_empty=True."""
    pq = _make_pq()
    assert pq.size() == 0, f"size={pq.size()}"
    assert pq.is_empty() is True


def tc20():
    """Dequeue đúng thứ tự ưu tiên: 3 BN khác severity → thứ tự B(1) → C(2) → A(3)."""
    pq = _make_pq()
    # Đặt tên A, B, C theo severity để kỳ vọng rõ ràng
    pA = Patient("BNA", "A", 30, 3, "08:00", reg_order=1)
    pB = Patient("BNB", "B", 30, 1, "08:00", reg_order=2)
    pC = Patient("BNC", "C", 30, 2, "08:00", reg_order=3)
    for p in [pA, pB, pC]:
        pq.enqueue(p)
    order = [pq.dequeue().patient_id for _ in range(3)]
    assert order == ["BNB", "BNC", "BNA"], f"Thứ tự thực tế: {order}"


def tc21():
    """contains() trước và sau dequeue: True trước khi lấy ra, False sau."""
    pq = _make_pq()
    p = Patient("BN001", "Test", 30, 1, "08:00", reg_order=1)
    pq.enqueue(p)
    assert pq.contains("BN001") is True
    pq.dequeue()
    assert pq.contains("BN001") is False


def tc22():
    """remove_by_id với ID không tồn tại → trả về None."""
    pq = _make_pq()
    result = pq.remove_by_id("BN_KHONG_TON_TAI")
    assert result is None, f"result={result}"


def tc23():
    """clear() xóa toàn bộ hàng đợi: sau clear → size=0, is_empty=True."""
    pq = _make_pq()
    for i in range(4):
        pq.enqueue(Patient(f"BN00{i}", f"N{i}", 30, i % 5 + 1, "08:00", reg_order=i+1))
    pq.clear()
    assert pq.size() == 0, f"size={pq.size()}"
    assert pq.is_empty() is True


def tc24():
    """Reinsert sau sửa severity: A từ sev=5→1 phải nhảy lên đầu hàng đợi."""
    pq = _make_pq()
    pA = Patient("BNA", "A", 30, 5, "08:00", reg_order=1)
    pB = Patient("BNB", "B", 30, 1, "09:00", reg_order=2)
    pq.enqueue(pA)
    pq.enqueue(pB)

    # Trước sửa: B (sev=1) ở đầu
    assert pq.peek().patient_id == "BNB"

    # Sửa A: sev=5 → 1, arr=08:00 < 09:00 → A phải ở đầu
    pA.severity = 1
    pq.reinsert(pA)
    assert pq.peek().patient_id == "BNA", (
        f"Sau reinsert, đỉnh phải là BNA nhưng là {pq.peek().patient_id}")


def tc25():
    """get_sorted_list() không làm đổi heap: đỉnh và size giữ nguyên."""
    pq = _make_pq()
    patients = [
        Patient("BN1", "X", 30, 3, "08:00", reg_order=1),
        Patient("BN2", "Y", 30, 1, "08:00", reg_order=2),
        Patient("BN3", "Z", 30, 2, "08:00", reg_order=3),
    ]
    for p in patients:
        pq.enqueue(p)

    top_before = pq.peek().patient_id
    size_before = pq.size()
    _ = pq.get_sorted_list()
    assert pq.peek().patient_id == top_before, "Đỉnh heap bị thay đổi sau get_sorted_list"
    assert pq.size() == size_before, "size bị thay đổi sau get_sorted_list"


def tc26():
    """save/load giữ toàn vẹn dữ liệu: thứ tự phục hồi 100%."""
    # Dùng file tạm để không ảnh hưởng dữ liệu thật
    tmp_dir = tempfile.mkdtemp()
    queue_file   = os.path.join(tmp_dir, "queue.csv")
    history_file = os.path.join(tmp_dir, "history.csv")

    pq1 = _make_pq()
    patients = [
        Patient("BN001", "Alpha",  45, 1, "08:00", reg_order=1),
        Patient("BN002", "Beta",   30, 2, "07:30", reg_order=2),
        Patient("BN003", "Gamma",  60, 1, "08:30", reg_order=3),
    ]
    for p in patients:
        pq1.enqueue(p)

    pq1.save_to_file(queue_file)

    # Load vào PriorityQueue mới
    pq2 = _make_pq()
    pq2.load_from_file(queue_file)

    # Kiểm tra số lượng và thứ tự ưu tiên
    assert pq2.size() == 3, f"size sau load={pq2.size()}"
    sorted_ids = [p.patient_id for p in pq2.get_sorted_list()]
    # Thứ tự: BN001(sev=1,08:00,reg=1) → BN003(sev=1,08:30,reg=3) → BN002(sev=2,07:30,reg=2)
    assert sorted_ids == ["BN001", "BN003", "BN002"], (
        f"Thứ tự sau load: {sorted_ids}")


# =============================================================================
# CHẠY TẤT CẢ TEST
# =============================================================================

def run_all():
    print("=" * 65)
    print("  KIỂM THỬ TỰ ĐỘNG — Hệ thống Quản lý Bệnh viện")
    print("=" * 65)

    groups = [
        ("GROUP A — MinHeap (TC-01 → TC-08)", [
            ("TC-01", "Insert 6 số, extract_min trả về thứ tự tăng dần",   tc01),
            ("TC-02", "Heap 1 phần tử: insert(42) → extract 42, rỗng",     tc02),
            ("TC-03", "peek_min() ×3 không thay đổi heap, size vẫn 3",      tc03),
            ("TC-04", "Xóa nút lá (x==9), còn lại [1,3,5,7]",              tc04),
            ("TC-05", "Xóa nút gốc (x==1), còn lại [3,5,7,9]",             tc05),
            ("TC-06", "Xóa phần tử không tồn tại → None, size không đổi",  tc06),
            ("TC-07", "find_all(x%2==0) trên [1..8] → [2,4,6,8]",          tc07),
            ("TC-08", "to_sorted_list() không phá vỡ heap",                 tc08),
        ]),
        ("GROUP B — Patient (TC-09 → TC-16)", [
            ("TC-09", "Severity nhỏ hơn được ưu tiên hơn",                  tc09),
            ("TC-10", "Cùng severity, đến sớm hơn được ưu tiên",            tc10),
            ("TC-11", "Cùng sev + arr, reg_order nhỏ hơn được ưu tiên",     tc11),
            ("TC-12", "__eq__ chỉ so sánh patient_id",                       tc12),
            ("TC-13", "Validate giờ đúng HH:MM: '13:45' → True",            tc13),
            ("TC-14", "Chuẩn hóa '7:05' → '07:05'",                         tc14),
            ("TC-15", "Từ chối giờ có phút > 59: '10:61'",                  tc15),
            ("TC-16", "Từ chối chuỗi không phải giờ: 'buoi sang'",          tc16),
        ]),
        ("GROUP C — PriorityQueue + Scheduler (TC-17 → TC-26)", [
            ("TC-17", "Tự gán reg_order khi enqueue (reg_order=0 → ≥1)",    tc17),
            ("TC-18", "Giữ nguyên reg_order đã có (reg_order=77)",          tc18),
            ("TC-19", "size() và is_empty() nhất quán với PQ mới",          tc19),
            ("TC-20", "Dequeue đúng thứ tự ưu tiên: B→C→A",                tc20),
            ("TC-21", "contains() True trước, False sau dequeue",           tc21),
            ("TC-22", "remove_by_id ID không tồn tại → None",              tc22),
            ("TC-23", "clear() → size=0, is_empty=True",                    tc23),
            ("TC-24", "Reinsert sau sửa severity: A sev=5→1 nhảy lên đầu", tc24),
            ("TC-25", "get_sorted_list() không thay đổi heap",              tc25),
            ("TC-26", "save/load giữ toàn vẹn dữ liệu và thứ tự",         tc26),
        ]),
    ]

    for group_name, cases in groups:
        print(f"\n{YELLOW}{group_name}{RESET}")
        print("─" * 65)
        for tc_id, desc, func in cases:
            _run(tc_id, desc, func)

    # ─── Tổng kết ───────────────────────────────────────────────────────────
    passed = sum(1 for _, ok, _ in _results if ok)
    failed = len(_results) - passed

    print("\n" + "=" * 65)
    print(f"  KẾT QUẢ: {passed}/{len(_results)} test case đạt", end="")
    if failed == 0:
        print(f"  {GREEN}— TẤT CẢ ĐẠT ✓{RESET}")
    else:
        print(f"  {RED}— {failed} THẤT BẠI{RESET}")
        print(f"\n  {RED}Test case thất bại:{RESET}")
        for tc_id, ok, desc in _results:
            if not ok:
                print(f"    [{tc_id}] {desc}")
    print("=" * 65)

    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
