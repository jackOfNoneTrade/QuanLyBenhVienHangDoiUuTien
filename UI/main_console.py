# =============================================================================
# UI/main_console.py
# Giao diện dòng lệnh (console) cho hệ thống quản lý hàng đợi bệnh viện.
#
# Nguyên tắc thiết kế:
#   - UI chỉ gọi Scheduler — TUYỆT ĐỐI không truy cập heap / linked list.
#   - Mọi validation nghiệp vụ nằm ở Scheduler; UI chỉ validate input rỗng
#     và kiểu dữ liệu thô trước khi truyền vào.
#   - Luồng: khởi động → load file → menu → Scheduler xử lý → lưu → hiển thị.
#
# Cấu trúc module:
#   ConsoleUI          — lớp chính, quản lý vòng lặp menu
#   _input_*           — các hàm nhập liệu có validate cơ bản
#   _menu_*            — các handler tương ứng 8 chức năng
#   run()              — điểm vào duy nhất
# =============================================================================

import os
import sys

from Algorithm.scheduler import Scheduler
from Data.patient        import SEVERITY_LABELS


# ─── HẰNG SỐ HIỂN THỊ ────────────────────────────────────────────────────────

W      = 60          # chiều rộng khung menu
SEP    = '─' * W
SEP2   = '═' * W
BANNER = r"""
  ██╗  ██╗ ██████╗ ███████╗██████╗ ██╗████████╗ █████╗ ██╗
  ██║  ██║██╔═══██╗██╔════╝██╔══██╗██║╚══██╔══╝██╔══██╗██║
  ███████║██║   ██║███████╗██████╔╝██║   ██║   ███████║██║
  ██╔══██║██║   ██║╚════██║██╔═══╝ ██║   ██║   ██╔══██║██║
  ██║  ██║╚██████╔╝███████║██║     ██║   ██║   ██║  ██║███████╗
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝     ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝
        Hệ thống Quản lý Hàng đợi Bệnh viện  v1.0
"""


# ─── TIỆN ÍCH CONSOLE ────────────────────────────────────────────────────────

def _clear():
    """Xóa màn hình (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')


def _pause():
    """Chờ người dùng nhấn Enter để tiếp tục."""
    input("\n  [ Nhấn Enter để quay lại menu... ]")


def _header(title: str):
    """In tiêu đề section."""
    print(f"\n{SEP2}")
    print(f"  {title}")
    print(SEP2)


def _ok(msg: str):
    print(f"\n  ✔  {msg}")


def _err(msg: str):
    print(f"\n  ✘  {msg}")


def _info(msg: str):
    print(f"  ℹ  {msg}")


# ─── HÀM NHẬP LIỆU CÓ KIỂM TRA CƠ BẢN ──────────────────────────────────────

def _input_str(prompt: str, allow_empty: bool = False) -> str | None:
    """
    Nhập chuỗi văn bản.
    Trả về None nếu người dùng nhập rỗng và allow_empty=False.
    """
    val = input(f"  {prompt}").strip()
    if not val and not allow_empty:
        return None
    return val


def _input_int(prompt: str, lo: int, hi: int) -> int | None:
    """
    Nhập số nguyên trong đoạn [lo, hi].
    Trả về None nếu không hợp lệ.
    """
    raw = input(f"  {prompt}").strip()
    if not raw:
        return None
    try:
        val = int(raw)
        if lo <= val <= hi:
            return val
        print(f"  ✘  Vui lòng nhập số từ {lo} đến {hi}.")
        return None
    except ValueError:
        print(f"  ✘  '{raw}' không phải số nguyên.")
        return None


def _input_optional_str(prompt: str) -> str | None:
    """Nhập chuỗi tuỳ chọn — trả về None nếu bỏ qua (Enter)."""
    raw = input(f"  {prompt}").strip()
    return raw if raw else None


def _severity_legend():
    """In bảng tra mức độ bệnh."""
    print(f"\n  {'Mức':<6} {'Ý nghĩa'}")
    print(f"  {'─'*20}")
    for lvl, label in SEVERITY_LABELS.items():
        print(f"  {lvl:<6} {label}")


# ─── LỚP CONSOLE UI ──────────────────────────────────────────────────────────

class ConsoleUI:
    """
    Giao diện dòng lệnh — lớp duy nhất trong UI layer.
    Mọi nghiệp vụ được uỷ quyền cho self._sched (Scheduler).
    """

    def __init__(self):
        self._sched = Scheduler()

    # ══════════════════════════════════════════════════════════════════════════
    # KHỞI ĐỘNG
    # ══════════════════════════════════════════════════════════════════════════

    def start(self):
        """Điểm vào: load dữ liệu rồi vào vòng lặp menu chính."""
        _clear()
        print(BANNER)
        print(f"  {SEP}")
        print("  Đang tải dữ liệu...")
        self._sched.loadData()
        print(f"  {SEP}")
        _pause()
        self._main_loop()

    # ══════════════════════════════════════════════════════════════════════════
    # VÒNG LẶP MENU CHÍNH
    # ══════════════════════════════════════════════════════════════════════════

    def _main_loop(self):
        """Vòng lặp hiển thị menu và điều hướng các chức năng."""
        MENU_ITEMS = [
            ("1", "Thêm bệnh nhân"),
            ("2", "Gọi khám (lấy ưu tiên cao nhất)"),
            ("3", "Xem hàng đợi hiện tại"),
            ("4", "Tìm kiếm bệnh nhân"),
            ("5", "Sửa thông tin bệnh nhân"),
            ("6", "Xóa bệnh nhân khỏi hàng đợi"),
            ("7", "Xem lịch sử đã khám"),
            ("8", "Thống kê hệ thống"),
            ("0", "Thoát"),
        ]

        HANDLERS = {
            "1": self._menu_add,
            "2": self._menu_call_next,
            "3": self._menu_view_queue,
            "4": self._menu_search,
            "5": self._menu_edit,
            "6": self._menu_delete,
            "7": self._menu_history,
            "8": self._menu_stats,
        }

        while True:
            _clear()
            # ── Tiêu đề ──
            print(f"\n{SEP2}")
            print(f"  BỆNH VIỆN — QUẢN LÝ HÀNG ĐỢI")
            waiting  = self._sched.count_waiting()
            examined = self._sched.count_examined()
            print(f"  Đang chờ: {waiting}  |  Đã khám: {examined}")
            print(SEP2)

            # ── Danh sách menu ──
            for code, label in MENU_ITEMS:
                bullet = "►" if code != "0" else "✕"
                print(f"  {bullet}  [{code}]  {label}")
            print(SEP)

            choice = input("  Chọn chức năng: ").strip()

            if choice == "0":
                _clear()
                print(f"\n{SEP2}")
                print("  Cảm ơn. Hẹn gặp lại!")
                print(SEP2)
                break

            handler = HANDLERS.get(choice)
            if handler:
                _clear()
                handler()
                _pause()
            else:
                print("\n  ✘  Lựa chọn không hợp lệ. Vui lòng thử lại.")
                _pause()

    # ══════════════════════════════════════════════════════════════════════════
    # [1] THÊM BỆNH NHÂN
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_add(self):
        _header("THÊM BỆNH NHÂN MỚI")
        _info(f"Mã BN tiếp theo sẽ là: {self._sched.get_next_id_preview()}")
        print()

        # Tên
        name = _input_str("Họ và tên bệnh nhân : ")
        if name is None:
            _err("Tên không được để trống.")
            return

        # Tuổi
        age = _input_int("Tuổi                : ", 1, 150)
        if age is None:
            return

        # Mức độ bệnh
        _severity_legend()
        severity = _input_int("\n  Mức độ bệnh (1-5)   : ", 1, 5)
        if severity is None:
            return

        # Giờ đến — tuỳ chọn
        arrival = _input_optional_str(
            "Giờ đến (HH:MM, Enter = hiện tại): "
        )

        # Giao cho Scheduler xử lý
        ok, msg, patient = self._sched.add_patient(name, age, severity, arrival)
        if ok:
            _ok(msg)
            if patient:
                print(f"\n  {'─'*46}")
                print(f"  Mã bệnh nhân   : {patient.patient_id}")
                print(f"  Họ tên         : {patient.name}")
                print(f"  Tuổi           : {patient.age}")
                sev_label = SEVERITY_LABELS.get(patient.severity, "")
                print(f"  Mức độ         : {patient.severity} - {sev_label}")
                print(f"  Giờ đến        : {patient.arrival_time}")
                print(f"  Thứ tự đăng ký : #{patient.reg_order}")
                print(f"  {'─'*46}")
        else:
            _err(msg)

    # ══════════════════════════════════════════════════════════════════════════
    # [2] GỌI KHÁM
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_call_next(self):
        _header("GỌI BỆNH NHÂN VÀO KHÁM")

        # Hiển thị trước để y tá xác nhận
        nxt = self._sched._queue.peek()    # chỉ xem, không lấy ra
        if nxt is None:
            _info("Hàng đợi đang trống. Không có bệnh nhân nào.")
            return

        label = SEVERITY_LABELS.get(nxt.severity, "")
        print(f"\n  Bệnh nhân tiếp theo:")
        print(f"  {'─'*46}")
        print(f"  Mã              : {nxt.patient_id}")
        print(f"  Họ tên          : {nxt.name}")
        print(f"  Tuổi            : {nxt.age}")
        print(f"  Mức độ          : {nxt.severity} - {label}")
        print(f"  Giờ đến         : {nxt.arrival_time}")
        print(f"  {'─'*46}")

        confirm = input("\n  Xác nhận gọi khám? (y/N): ").strip().lower()
        if confirm not in ("y", "yes", "có", "co"):
            _info("Đã huỷ.")
            return

        patient = self._sched.call_next()
        if patient:
            _ok(f"Đã gọi: {patient.name} [{patient.patient_id}]")
            remaining = self._sched.count_waiting()
            _info(f"Còn lại trong hàng đợi: {remaining} người.")
        else:
            _err("Hàng đợi rỗng (có thể vừa bị thay đổi).")

    # ══════════════════════════════════════════════════════════════════════════
    # [3] XEM HÀNG ĐỢI
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_view_queue(self):
        _header("DANH SÁCH BỆNH NHÂN ĐANG CHỜ")
        self._sched.display_queue()

    # ══════════════════════════════════════════════════════════════════════════
    # [4] TÌM KIẾM
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_search(self):
        _header("TÌM KIẾM BỆNH NHÂN")

        print("  Tìm trong:")
        print("  [1]  Hàng đợi đang chờ — theo Mã BN  (O(1))")
        print("  [2]  Hàng đợi đang chờ — theo Tên    (O(N))")
        print("  [3]  Lịch sử đã khám   — theo Mã BN  (O(N))")
        print(SEP)

        mode = input("  Chọn (1/2/3): ").strip()

        if mode == "1":
            self._search_queue_by_id()
        elif mode == "2":
            self._search_queue_by_name()
        elif mode == "3":
            self._search_history_by_id()
        else:
            _err("Lựa chọn không hợp lệ.")

    def _search_queue_by_id(self):
        pid = _input_str("Nhập Mã BN (ví dụ BN0001): ")
        if pid is None:
            _err("Mã không được để trống.")
            return
        patient = self._sched.search_by_id(pid)
        if patient:
            label = SEVERITY_LABELS.get(patient.severity, "")
            print(f"\n  {'─'*46}")
            print(f"  Kết quả tìm kiếm — mã '{pid}':")
            print(f"  {'─'*46}")
            print(f"  Mã              : {patient.patient_id}")
            print(f"  Họ tên          : {patient.name}")
            print(f"  Tuổi            : {patient.age}")
            print(f"  Mức độ          : {patient.severity} - {label}")
            print(f"  Giờ đến         : {patient.arrival_time}")
            print(f"  Thứ tự đăng ký  : #{patient.reg_order}")
            print(f"  {'─'*46}")
        else:
            _info(f"Không tìm thấy '{pid}' trong hàng đợi.")

    def _search_queue_by_name(self):
        name = _input_str("Nhập tên (một phần): ")
        if name is None:
            _err("Tên không được để trống.")
            return
        results = self._sched.search_by_name(name)
        if not results:
            _info(f"Không tìm thấy bệnh nhân nào tên chứa '{name}'.")
            return
        print(f"\n  Tìm thấy {len(results)} bệnh nhân:\n")
        print(f"  {'Mã BN':<9} {'Tên':<22} {'Tuổi':<6} {'Mức độ':<16} {'Giờ đến'}")
        print(f"  {'─'*62}")
        for p in results:
            label = SEVERITY_LABELS.get(p.severity, "")
            print(f"  {p.patient_id:<9} {p.name:<22} {p.age:<6} "
                  f"{p.severity}-{label:<14} {p.arrival_time}")

    def _search_history_by_id(self):
        pid = _input_str("Nhập Mã BN cần tra cứu lịch sử: ")
        if pid is None:
            _err("Mã không được để trống.")
            return
        records = self._sched.search_history_by_id(pid)
        if not records:
            _info(f"Không tìm thấy lịch sử nào cho '{pid}'.")
            return
        print(f"\n  Lịch sử khám của '{pid}' ({len(records)} lượt):\n")
        print(f"  {'#':<4} {'Tên':<22} {'Tuổi':<6} {'Mức độ':<16} {'Giờ đến':<10} {'Giờ khám'}")
        print(f"  {'─'*70}")
        for i, rec in enumerate(records, 1):
            p     = rec.patient
            label = SEVERITY_LABELS.get(p.severity, "")
            print(f"  {i:<4} {p.name:<22} {p.age:<6} "
                  f"{p.severity}-{label:<14} {p.arrival_time:<10} {rec.time_called}")

    # ══════════════════════════════════════════════════════════════════════════
    # [5] SỬA THÔNG TIN
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_edit(self):
        _header("SỬA THÔNG TIN BỆNH NHÂN")

        pid = _input_str("Nhập Mã BN cần sửa: ")
        if pid is None:
            _err("Mã không được để trống.")
            return

        # Kiểm tra tồn tại trước
        current = self._sched.search_by_id(pid)
        if current is None:
            _err(f"Không tìm thấy '{pid}' trong hàng đợi.")
            return

        # Hiển thị thông tin hiện tại
        label = SEVERITY_LABELS.get(current.severity, "")
        print(f"\n  Thông tin hiện tại:")
        print(f"  {'─'*46}")
        print(f"  Tên    : {current.name}")
        print(f"  Tuổi   : {current.age}")
        print(f"  Mức độ : {current.severity} - {label}")
        print(f"  {'─'*46}")
        print("  (Enter để giữ nguyên giá trị cũ)\n")

        # Nhập giá trị mới — tất cả đều tuỳ chọn
        new_name = _input_optional_str(f"  Tên mới   [{current.name}]: ")
        new_age_raw  = _input_optional_str(f"  Tuổi mới  [{current.age}]: ")
        _severity_legend()
        new_sev_raw  = _input_optional_str(f"\n  Mức mới   [{current.severity}]: ")

        # Chuyển đổi kiểu
        new_age = None
        if new_age_raw is not None:
            try:
                new_age = int(new_age_raw)
            except ValueError:
                _err(f"Tuổi '{new_age_raw}' không hợp lệ.")
                return

        new_sev = None
        if new_sev_raw is not None:
            try:
                new_sev = int(new_sev_raw)
            except ValueError:
                _err(f"Mức độ '{new_sev_raw}' không hợp lệ.")
                return

        # Giao cho Scheduler
        ok, msg = self._sched.edit_patient(
            pid,
            new_name=new_name if new_name else None,
            new_age=new_age,
            new_severity=new_sev
        )
        _ok(msg) if ok else _err(msg)

    # ══════════════════════════════════════════════════════════════════════════
    # [6] XÓA BỆNH NHÂN
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_delete(self):
        _header("XÓA BỆNH NHÂN KHỎI HÀNG ĐỢI")

        pid = _input_str("Nhập Mã BN cần xóa: ")
        if pid is None:
            _err("Mã không được để trống.")
            return

        # Hiển thị thông tin để xác nhận
        patient = self._sched.search_by_id(pid)
        if patient is None:
            _err(f"Không tìm thấy '{pid}' trong hàng đợi.")
            return

        label = SEVERITY_LABELS.get(patient.severity, "")
        print(f"\n  Bệnh nhân cần xóa:")
        print(f"  {'─'*46}")
        print(f"  Mã     : {patient.patient_id}")
        print(f"  Tên    : {patient.name}")
        print(f"  Tuổi   : {patient.age}")
        print(f"  Mức độ : {patient.severity} - {label}")
        print(f"  Giờ đến: {patient.arrival_time}")
        print(f"  {'─'*46}")

        confirm = input("\n  Xác nhận xóa? (y/N): ").strip().lower()
        if confirm not in ("y", "yes", "có", "co"):
            _info("Đã huỷ.")
            return

        ok, msg = self._sched.remove_patient(pid)
        _ok(msg) if ok else _err(msg)

    # ══════════════════════════════════════════════════════════════════════════
    # [7] XEM LỊCH SỬ
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_history(self):
        _header("LỊCH SỬ BỆNH NHÂN ĐÃ KHÁM")

        total = self._sched.count_examined()
        if total == 0:
            _info("Chưa có bệnh nhân nào được khám trong phiên này.")
            return

        print(f"  Tổng số lượt đã khám: {total}\n")
        print("  Hiển thị:")
        print("  [1]  Toàn bộ lịch sử")
        print("  [2]  Tìm theo Mã BN")
        print(SEP)

        mode = input("  Chọn (1/2): ").strip()

        if mode == "1":
            self._sched.display_history()
        elif mode == "2":
            self._search_history_by_id()
        else:
            _err("Lựa chọn không hợp lệ.")

    # ══════════════════════════════════════════════════════════════════════════
    # [8] THỐNG KÊ
    # ══════════════════════════════════════════════════════════════════════════

    def _menu_stats(self):
        _header("THỐNG KÊ HỆ THỐNG")
        stats = self._sched.get_statistics()

        W2 = 48
        print(f"\n  {'═'*W2}")
        print(f"  {'Chỉ số':<30} {'Giá trị':>10}")
        print(f"  {'─'*W2}")
        print(f"  {'Mã BN tiếp theo':<30} {stats['next_id']:>10}")
        print(f"  {'Đang chờ khám':<30} {stats['total_waiting']:>10}")
        print(f"  {'Đã khám xong':<30} {stats['total_examined']:>10}")
        print(f"  {'═'*W2}")

        print(f"\n  Phân bố bệnh nhân đang chờ theo mức độ:\n")
        print(f"  {'Mức':<6} {'Loại':<14} {'SL':>4}  {'Biểu đồ'}")
        print(f"  {'─'*W2}")
        for lvl in range(1, 6):
            count = stats['by_severity'][lvl]
            label = SEVERITY_LABELS[lvl]
            bar   = "█" * min(count, 25)
            extra = f"(+{count-25})" if count > 25 else ""
            print(f"  {lvl:<6} {label:<14} {count:>4}  {bar}{extra}")
        print(f"  {'─'*W2}")

        # Bệnh nhân tiếp theo
        nxt = stats['next_patient']
        print(f"\n  Bệnh nhân tiếp theo:")
        if nxt:
            lbl = SEVERITY_LABELS.get(nxt.severity, "")
            print(f"  {'─'*46}")
            print(f"  Mã     : {nxt.patient_id}")
            print(f"  Tên    : {nxt.name}")
            print(f"  Mức độ : {nxt.severity} - {lbl}")
            print(f"  Giờ đến: {nxt.arrival_time}")
            print(f"  {'─'*46}")
        else:
            print(f"  (Không có ai đang chờ)")


# ══════════════════════════════════════════════════════════════════════════════
# ĐIỂM VÀO
# ══════════════════════════════════════════════════════════════════════════════

def run():
    """Khởi chạy ứng dụng console."""
    try:
        ui = ConsoleUI()
        ui.start()
    except KeyboardInterrupt:
        print("\n\n  Đã ngắt chương trình. Tạm biệt!")
        sys.exit(0)


if __name__ == "__main__":
    run()
