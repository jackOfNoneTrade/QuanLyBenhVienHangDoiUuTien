# =============================================================================
# Data/patient.py
# Kiểu dữ liệu mô tả một bệnh nhân.
#
# Quy tắc so sánh ưu tiên (dùng bởi MinHeap):
#   1. severity nhỏ hơn → ưu tiên hơn  (mức 1 = nguy kịch)
#   2. Cùng severity → arrival_time nhỏ hơn → ưu tiên hơn  (đến sớm hơn)
#   3. Cùng severity VÀ cùng arrival_time → reg_order nhỏ hơn → ưu tiên hơn
#      (đăng ký trước thì khám trước — tie-break cuối cùng, luôn duy nhất)
#
# Lưu ý format arrival_time:
#   Phải là "HH:MM" với padding số 0 (ví dụ "09:00" chứ không phải "9:00").
#   So sánh string chỉ đúng khi format đồng nhất. Validation nằm ở
#   Scheduler._validate() để đảm bảo dữ liệu nhập vào luôn hợp lệ.
# =============================================================================

import re

SEVERITY_LABELS = {
    1: "Nguy kịch",
    2: "Nặng",
    3: "Trung bình",
    4: "Nhẹ",
    5: "Rất nhẹ"
}

# Regex kiểm tra format HH:MM (00:00 – 23:59) phòng trường hợp tay nhanh hơn não
_TIME_RE = re.compile(r'^([01]\d|2[0-3]):[0-5]\d$')

# Các cột trong file CSV hàng đợi
QUEUE_CSV_FIELDS = ['PatientID', 'Name', 'Age', 'SeverityScore',
                    'ArrivalTime', 'RegOrder']


def validate_arrival_time(time_str: str) -> tuple[bool, str]:
    """
    Kiểm tra chuỗi giờ đến có đúng format HH:MM không.

    Trả về: (True, chuỗi đã chuẩn hoá) nếu hợp lệ,
            (False, thông báo lỗi)      nếu không hợp lệ.

    Ví dụ:
        "9:00"  → False  (thiếu padding)
        "09:00" → True
        "25:00" → False  (giờ không tồn tại)
    """
    s = str(time_str).strip()
    if _TIME_RE.match(s):
        return True, s
    # Thử tự-fix "H:MM" → "0H:MM" để thân thiện hơn với người dùng
    if re.match(r'^\d:[0-5]\d$', s):
        fixed = '0' + s
        if _TIME_RE.match(fixed):
            return True, fixed
    return False, f"Giờ đến '{time_str}' không hợp lệ — dùng định dạng HH:MM (ví dụ 09:30)."


class Patient:
    """
    Mô tả một bệnh nhân trong hệ thống quản lý bệnh viện.

    Thuộc tính:
        patient_id   (str) : Mã bệnh nhân tự động, ví dụ "BN0001"
        name         (str) : Họ và tên đầy đủ
        age          (int) : Tuổi
        severity     (int) : Mức độ bệnh — 1 (nguy kịch) đến 5 (rất nhẹ)
        arrival_time (str) : Giờ đến khám, định dạng "HH:MM" (luôn có padding)
        reg_order    (int) : Số thứ tự đăng ký toàn hệ thống (tự động, tăng dần)
                             Dùng làm tie-breaker khi severity và arrival_time bằng nhau.
    """

    def __init__(self, patient_id, name, age, severity, arrival_time,
                 reg_order=0):
        self.patient_id   = str(patient_id).strip()
        self.name         = str(name).strip()
        self.age          = int(age)
        self.severity     = int(severity)
        self.arrival_time = str(arrival_time).strip()
        self.reg_order    = int(reg_order)   # thứ tự đăng ký, luôn duy nhất

    #  SO SÁNH 

    def __lt__(self, other):
        """
        Bệnh nhân A < B nghĩa là A được ưu tiên hơn B.

        Quy tắc (theo thứ tự ưu tiên):
            1. severity nhỏ hơn → ưu tiên hơn
            2. Cùng severity → arrival_time nhỏ hơn → ưu tiên hơn
            3. Cùng severity + arrival_time → reg_order nhỏ hơn → ưu tiên hơn

        reg_order là số nguyên tăng dần, luôn duy nhất trong một phiên.
        → Không bao giờ có trường hợp __lt__ và __gt__ đều False (không bao giờ
          thực sự "bằng nhau" về thứ tự ưu tiên), tránh hành vi undefined trong heap.

        Ví dụ:
            BN0003 sev=1 08:00 reg=3  vs  BN0005 sev=1 08:00 reg=5
            → BN0003 < BN0005 → BN0003 được khám trước (đăng ký trước)
        """
        if self.severity != other.severity:
            return self.severity < other.severity
        if self.arrival_time != other.arrival_time:
            return self.arrival_time < other.arrival_time
        return self.reg_order < other.reg_order

    def __eq__(self, other):
        """Hai bệnh nhân bằng nhau khi và chỉ khi cùng patient_id."""
        if not isinstance(other, Patient):
            return False
        return self.patient_id == other.patient_id

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other

    # HIỂN THỊ 

    def __str__(self):
        label = SEVERITY_LABELS.get(self.severity, str(self.severity))
        return (f"[{self.patient_id}] {self.name} | "
                f"Tuổi: {self.age} | "
                f"Mức: {label} ({self.severity}) | "
                f"Giờ đến: {self.arrival_time} | "
                f"Đăng ký #{self.reg_order}")

    def __repr__(self):
        return (f"Patient(id={self.patient_id}, sev={self.severity}, "
                f"arr={self.arrival_time}, reg={self.reg_order})")

    #  CHUYỂN ĐỔI DỮ LIỆU

    def to_dict(self):
        """Chuyển bệnh nhân thành dict để ghi CSV."""
        return {
            'PatientID'    : self.patient_id,
            'Name'         : self.name,
            'Age'          : self.age,
            'SeverityScore': self.severity,
            'ArrivalTime'  : self.arrival_time,
            'RegOrder'     : self.reg_order
        }

    @staticmethod
    def from_dict(row):
        """Tạo Patient từ một dòng dict đọc từ CSV."""
        return Patient(
            patient_id   = row['PatientID'],
            name         = row['Name'],
            age          = int(row['Age']),
            severity     = int(row['SeverityScore']),
            arrival_time = row['ArrivalTime'],
            reg_order    = int(row.get('RegOrder', 0))
        )

    def to_display_row(self):
        """Trả về tuple để hiển thị trong Treeview của Tkinter."""
        label = SEVERITY_LABELS.get(self.severity, str(self.severity))
        return (self.patient_id, self.name, self.age,
                f"{self.severity} - {label}", self.arrival_time)



if __name__ == "__main__":
    print("=== Test Patient ===\n")

    p1 = Patient("BN0001", "Nguyen Van An",  45, 1, "08:00", reg_order=1)
    p2 = Patient("BN0002", "Tran Thi Binh",  30, 2, "07:30", reg_order=2)
    p3 = Patient("BN0003", "Le Van Cuong",   60, 1, "08:30", reg_order=3)
    p4 = Patient("BN0004", "Pham Thi Dung",  25, 1, "08:00", reg_order=4)

    print("Thông tin bệnh nhân:")
    for p in [p1, p2, p3, p4]:
        print(" ", p)

    print("\nKiểm tra so sánh ưu tiên:")
    print(f"  BN0001 (sev=1, 08:00, reg=1) < BN0002 (sev=2, 07:30, reg=2)?")
    print(f"  → {p1 < p2}  Kỳ vọng: True  (nặng hơn)")

    print(f"  BN0001 (sev=1, 08:00, reg=1) < BN0003 (sev=1, 08:30, reg=3)?")
    print(f"  → {p1 < p3}  Kỳ vọng: True  (cùng severity, đến trước)")

    print(f"  BN0001 (sev=1, 08:00, reg=1) < BN0004 (sev=1, 08:00, reg=4)?")
    print(f"  → {p1 < p4}  Kỳ vọng: True  (cùng sev+arr, đăng ký trước)")

    print(f"  BN0004 (sev=1, 08:00, reg=4) < BN0001 (sev=1, 08:00, reg=1)?")
    print(f"  → {p4 < p1}  Kỳ vọng: False (đăng ký sau)")

    print(f"  BN0001 == BN0001? {p1 == p1}  Kỳ vọng: True")
    print(f"  BN0001 == BN0004? {p1 == p4}  Kỳ vọng: False (khác ID)")

    print("\nKiểm tra validate_arrival_time:")
    for t in ["09:00", "9:00", "25:00", "08:60", "abc"]:
        ok, result = validate_arrival_time(t)
        print(f"  '{t}' → {'OK: ' + result if ok else 'ERR: ' + result}")

    print("\n✓ Tất cả test Patient hoàn thành.")
