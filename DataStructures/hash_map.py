# hash_map.py
#
# Cung cấp các cấu trúc HashMap dùng trong hệ thống quản lý bệnh viện.
#
# Thành phần:
#   - _ChainHashMap  : HashMap Separate Chaining dùng minh hoạ.
#   - PatientHashMap : Quản lý bệnh nhân theo patient_id.
#   - HashMap        : HashMap key-value tổng quát.
#
# Độ phức tạp trung bình:
#   - Thêm      : O(1)
#   - Tra cứu   : O(1)
#   - Xoá       : O(1)

from __future__ import annotations
from typing import Iterator, Optional

# Mảng băm separate Chaining

class _ChainHashMap:
    """
    Bảng băm Separate Chaining

    Mục đích: minh hoạ cơ chế hàm băm, collision, rehash để debug_info()
    và show_buckets() của PatientHashMap có thể trực quan hoá nội bộ.
    """

    _LOAD_MAX = 0.75   # ngưỡng load factor — vượt qua thì rehash

    def __init__(self, capacity: int = 16):
        self._cap   = capacity
        # Mỗi bucket là list of (key, value) — Separate Chaining
        self._table: list[list] = [[] for _ in range(self._cap)]
        self._size  = 0

    #  Hàm băm 

    def _index(self, key: str) -> int:
        """
        Ánh xạ key → chỉ số bucket.

        hash() tích hợp của Python (tối ưu C), abs() để tránh index âm.
        Modulo với _cap → đảm bảo index nằm trong [0, _cap).

            "BN0001"  →  hash("BN0001") = -6153...  →  abs = 6153...
                      →  6153... % 16 = 9   →  bucket[9]
        """
        return abs(hash(key)) % self._cap

    # CRUD 

    def put(self, key: str, value) -> None:
        """
        Chèn hoặc cập nhật (key, value).   O(1) trung bình.

        Quy trình:
          1. Tính index = hash(key) % capacity.
          2. Duyệt bucket[index] tìm key cũ → nếu có thì cập nhật.
          3. Nếu key mới → append vào bucket, tăng _size.
          4. Nếu load factor vượt ngưỡng → _rehash().
        """
        idx = self._index(key)
        bucket = self._table[idx]

        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)   # cập nhật key đã có
                return

        bucket.append((key, value))         # key mới → thêm vào cuối bucket
        self._size += 1

        if self._size / self._cap > self._LOAD_MAX:
            self._rehash()

    def get(self, key: str, sentinel=object()):
        """
        Tra cứu theo key.   O(1) trung bình.

        Dùng sentinel để phân biệt "không tìm thấy" với value=None.
        Trả về giá trị nếu tìm thấy, None nếu không có.
        """
        idx = self._index(key)
        for k, v in self._table[idx]:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> bool:
        """Xoá theo key.   O(1) trung bình.   Trả về True nếu tìm thấy."""
        idx = self._index(key)
        bucket = self._table[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def contains(self, key: str) -> bool:
        return self.get(key) is not None

    #  Rehashing 

    def _rehash(self) -> None:
        """
        Nhân đôi số bucket, băm lại tất cả phần tử.   O(N).

        Tại sao cần rehash?
          Khi load factor cao, nhiều bucket chứa nhiều phần tử
          → chuỗi xung đột dài → tra cứu chậm dần về O(N).
          Nhân đôi mảng dàn đều lại các phần tử → phục hồi O(1).

        Amortised O(1): rehash xảy ra ngày càng ít hơn (lần rehash thứ k
        xử lý ~2^k phần tử, nhưng đã thực hiện ~2^k thao tác kể từ lần
        trước) → chi phí trung bình mỗi put vẫn là O(1).
        """
        old_table  = self._table
        self._cap  = self._cap * 2
        self._table = [[] for _ in range(self._cap)]
        self._size  = 0

        for bucket in old_table:
            for key, value in bucket:
                self.put(key, value)   # băm lại với cap mới

    #  Thống kê 

    def stats(self) -> dict:
        lengths   = [len(b) for b in self._table]
        non_empty = [l for l in lengths if l > 0]
        return {
            'capacity'         : self._cap,
            'size'             : self._size,
            'load_factor'      : round(self._size / self._cap, 3),
            'non_empty_buckets': len(non_empty),
            'max_chain_len'    : max(lengths, default=0),
            'avg_chain_len'    : round(sum(non_empty)/len(non_empty), 2) if non_empty else 0,
        }

    def __len__(self):
        return self._size

# PatientHashMap — lớp CHÍNH dùng trong hệ thống

class PatientHashMap:
    """
    Bảng băm lưu cặp (patient_id → Patient).

    Triển khai bằng cách BỌC dict tích hợp của Python — tối ưu C-level,
    không có bảng băm thuần Python nào nhanh hơn trong CPython.

    Cơ chế hoạt động:
      • Tra cứu: hash(patient_id) → index → đọc trực tiếp → O(1).
      • Không cần duyệt vòng lặp như linked list hay array.

    Ngoài ra, lớp duy trì _demo (_ChainHashMap) để minh hoạ nội bộ
    bảng băm khi gọi debug_info() hoặc show_buckets()

    Phương thức chính:
        register(patient)       thêm / cập nhật           O(1)
        lookup(patient_id)      tra cứu theo ID            O(1)
        unregister(patient_id)  xoá                        O(1)
        contains(patient_id)    kiểm tra tồn tại           O(1)
        all_patients()          danh sách toàn bộ          O(N)
        debug_info()            thống kê bucket của _demo
        show_buckets()          in biểu đồ phân phối bucket
    """

    def __init__(self):
        # ── Bảng băm chính (production) 
        self._store: dict = {}          # { patient_id (str) : Patient }

        # ── Bảng băm minh hoạ (giáo khoa)
        # Được đồng bộ với _store ở mọi thao tác ghi để debug_info() chính xác.
        self._demo = _ChainHashMap(capacity=16)

    # THÊM / CẬP NHẬT

    def register(self, patient) -> None:
        """
        Đăng ký bệnh nhân vào registry.   O(1).

        Nếu patient_id đã tồn tại → ghi đè (cập nhật thông tin).
        Ném TypeError nếu đối tượng truyền vào không có patient_id.

        Cơ chế — dict của Python:
            self._store["BN0001"] = patient
            → Python tính hash("BN0001"), tìm slot, ghi value.
            → Không cần duyệt, không cần so sánh với các key khác.
        """
        if not hasattr(patient, 'patient_id'):
            raise TypeError(
                f"Chỉ nhận đối tượng Patient; nhận được {type(patient).__name__}.")

        pid = patient.patient_id
        self._store[pid] = patient    # O(1) — dict Python
        self._demo.put(pid, patient)  # đồng bộ bảng băm minh hoạ


    # TRA CỨU

    def lookup(self, patient_id: str) -> Optional[object]:
        """
        Tìm bệnh nhân theo ID.   O(1).

        Trả về đối tượng Patient, hoặc None nếu không tìm thấy.

        Cơ chế:
            Python tính hash("BN0042") → tìm slot trong mảng nội bộ của dict
            → đọc value trực tiếp. Không cần vòng lặp duyệt toàn bộ.

        So sánh với linked list:
            Linked list: phải while curr is not None → O(N).
            HashMap    : hash → index → đọc         → O(1).
        """
        return self._store.get(patient_id)   # trả None nếu không có

    def lookup_or_raise(self, patient_id: str):
        """Tìm bệnh nhân; ném KeyError nếu không tìm thấy."""
        patient = self._store.get(patient_id)
        if patient is None:
            raise KeyError(
                f"Không tìm thấy '{patient_id}' trong registry.")
        return patient

    def contains(self, patient_id: str) -> bool:
        """
        Kiểm tra patient_id có trong registry không.   O(1).

        Dùng toán tử `in` của dict — gọi hash() và tra bảng, không duyệt.
        """
        return patient_id in self._store


    # XOÁ

    def unregister(self, patient_id: str) -> bool:
        """
        Xoá bệnh nhân khỏi registry.   O(1).

        Trả về True nếu tìm thấy và đã xoá, False nếu không có.
        Gọi sau khi bệnh nhân hoàn tất khám và không cần tra cứu nữa.
        """
        if patient_id in self._store:
            del self._store[patient_id]
            self._demo.delete(patient_id)
            return True
        return False


    # DUYỆT

    def all_patients(self) -> list:
        """Danh sách tất cả Patient theo thứ tự đăng ký.   O(N)."""
        return list(self._store.values())

    def all_ids(self) -> list[str]:
        """Danh sách tất cả patient_id theo thứ tự đăng ký.   O(N)."""
        return list(self._store.keys())

    def items(self) -> Iterator[tuple[str, object]]:
        """Duyệt qua tất cả cặp (patient_id, Patient).   O(N)."""
        return iter(self._store.items())

    # DEBUG / GIÁO KHOA

    def debug_info(self) -> dict:
        """
        Trả về thống kê nội bộ của _ChainHashMap minh hoạ.

        Ví dụ output:
            capacity          : 16     ← tổng số bucket hiện có
            size              : 5      ← số cặp đang lưu
            load_factor       : 0.313  ← α = size/capacity; > 0.75 → rehash
            non_empty_buckets : 5      ← bao nhiêu bucket có dữ liệu
            max_chain_len     : 1      ← chuỗi xung đột dài nhất
            avg_chain_len     : 1.0    ← trung bình chiều dài chuỗi

        Khi max_chain_len >> 1 → nhiều xung đột → tra cứu chậm hơn O(1).
        Với load_factor ≤ 0.75 và hash tốt, max_chain_len thường bằng 1–2.
        """
        return self._demo.stats()

    def show_buckets(self) -> None:
        """
        In biểu đồ phân phối bucket ra stdout.

        Minh hoạ trực quan vị trí của từng key trong bảng băm,
        và xung đột (nhiều key trong cùng bucket).

        Ví dụ output:
            ── Phân phối bucket (capacity=16, size=5, load=31.25%) ──
            Bucket[  3]  █          ← BN0002
            Bucket[  7]  ██         ← BN0001, BN0099   (xung đột!)
            Bucket[ 11]  █          ← BN0003
        """
        s = self._demo.stats()
        print(f"\n── Phân phối bucket "
              f"(capacity={s['capacity']}, size={s['size']}, "
              f"load={s['load_factor']:.2%}) ──")
        for i, bucket in enumerate(self._demo._table):
            if bucket:
                keys  = ', '.join(k for k, _ in bucket)
                bar   = '█' * len(bucket)
                clash = '  ← XUNG ĐỘT' if len(bucket) > 1 else ''
                print(f"  Bucket[{i:3d}]  {bar:12s}  ← {keys}{clash}")
        print()

    # MAGIC METHODS

    def __len__(self) -> int:
        return len(self._store)

    def __bool__(self) -> bool:
        return bool(self._store)

    def __contains__(self, patient_id: str) -> bool:
        return self.contains(patient_id)

    def __getitem__(self, patient_id: str):
        """registry["BN0001"] → lookup_or_raise"""
        return self.lookup_or_raise(patient_id)

    def __setitem__(self, patient_id: str, patient) -> None:
        """registry["BN0001"] = patient → register()"""
        self.register(patient)

    def __delitem__(self, patient_id: str) -> None:
        """del registry["BN0001"] → unregister()"""
        if not self.unregister(patient_id):
            raise KeyError(f"'{patient_id}' không có trong registry.")

    def __iter__(self) -> Iterator[str]:
        """Duyệt qua tất cả patient_id."""
        return iter(self._store)

    def __str__(self) -> str:
        if not self._store:
            return "PatientHashMap { }"
        lines = [f"  {pid} → {p!r}" for pid, p in self._store.items()]
        return "PatientHashMap {\n" + "\n".join(lines) + "\n}"

    def __repr__(self) -> str:
        return f"PatientHashMap(size={len(self._store)})"


# KIỂM TRA THỦ CÔNG
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from patient import Patient

    print("=" * 60)
    print("  KIỂM TRA PatientHashMap")
    print("=" * 60)

    registry = PatientHashMap()
    print(f"\n[1] Khởi tạo: {repr(registry)}")
    print(f"    Rỗng? {not registry}  |  len={len(registry)}")
    assert len(registry) == 0

    # ── Tạo dữ liệu mẫu ──
    patients = [
        Patient("BN0001", "Nguyen Van An",  45, 1, "08:00", reg_order=1),
        Patient("BN0002", "Tran Thi Binh",  30, 2, "07:30", reg_order=2),
        Patient("BN0003", "Le Van Cuong",   60, 1, "08:30", reg_order=3),
        Patient("BN0004", "Pham Thi Dung",  25, 3, "09:00", reg_order=4),
        Patient("BN0005", "Hoang Van Em",   38, 4, "09:15", reg_order=5),
    ]

    # ── register: O(1) ──
    print("\n[2] register() — O(1), hash(id) → index → ghi vào slot:")
    for p in patients:
        registry.register(p)
        print(f"    register({p.patient_id})  →  len={len(registry)}")
    assert len(registry) == 5

    # ── lookup: O(1) ──
    print("\n[3] lookup() — O(1), hash(id) → đọc trực tiếp, không duyệt:")
    for pid in ["BN0001", "BN0003", "BN9999"]:
        result = registry.lookup(pid)
        print(f"    lookup('{pid}') → {result}")
    assert registry.lookup("BN0001").patient_id == "BN0001"
    assert registry.lookup("BN9999") is None

    # ── contains / toán tử in: O(1) ──
    print("\n[4] contains() — O(1), toán tử 'in':")
    print(f"    'BN0002' in registry : {'BN0002' in registry}   (kỳ vọng True)")
    print(f"    'BN9999' in registry : {'BN9999' in registry}   (kỳ vọng False)")
    assert "BN0002" in registry
    assert "BN9999" not in registry

    # ── toán tử [] ──
    print("\n[5] Toán tử [] (giống dict):")
    print(f"    registry['BN0004'] → {registry['BN0004']}")

    # ── register ghi đè (update) ──
    print("\n[6] register() ghi đè — cập nhật BN0001 severity 1→3:")
    p_updated = Patient("BN0001", "Nguyen Van An", 45, 3, "08:00", reg_order=1)
    registry.register(p_updated)
    assert registry.lookup("BN0001").severity == 3
    print(f"    Sau cập nhật: {registry.lookup('BN0001')}")
    assert len(registry) == 5   # số lượng không thay đổi

    # ── unregister: O(1) ──
    print("\n[7] unregister() — O(1):")
    ok = registry.unregister("BN0002")
    print(f"    unregister('BN0002'): {ok}   (kỳ vọng True)")
    print(f"    unregister('BN9999'): {registry.unregister('BN9999')}   (kỳ vọng False)")
    assert ok and len(registry) == 4
    assert "BN0002" not in registry

    # ── all_ids / all_patients ──
    print("\n[8] all_ids() — thứ tự đăng ký:")
    print(f"    {registry.all_ids()}")

    # ── debug_info + show_buckets ──
    print("\n[9] debug_info() — thống kê bảng băm _ChainHashMap minh hoạ:")
    for k, v in registry.debug_info().items():
        print(f"    {k:22s}: {v}")

    registry.show_buckets()

    # ── TypeError ──
    print("[10] Kiểm tra TypeError khi register đối tượng không hợp lệ:")
    try:
        registry.register("không phải Patient")
    except TypeError as e:
        print(f"    TypeError đúng: {e}")

    print("\n✓ Tất cả kiểm tra PatientHashMap hoàn thành.\n")


# HashMap — bảng băm generic key-value dùng trong Scheduler
class HashMap:
    """
    Bảng băm key-value generic, bọc Python dict tích hợp.

    Interface:
        put(key, value)   → thêm / cập nhật       O(1)
        get(key)          → tra cứu                O(1), None nếu không có
        has(key)          → kiểm tra tồn tại       O(1)
        delete(key)       → xóa                    O(1)
        clear()           → xóa toàn bộ            O(1)
        size()            → số phần tử             O(1)

    Dùng trong Scheduler để lưu cặp (patient_id → Patient),
    phân biệt với PatientHashMap (kiểm tra kiểu, có chế độ giáo khoa).
    """

    def __init__(self):
        self._store: dict = {}

    def put(self, key: str, value) -> None:
        """Thêm hoặc cập nhật cặp (key, value). O(1)."""
        self._store[key] = value

    def get(self, key: str):
        """Tra cứu theo key, trả None nếu không có. O(1)."""
        return self._store.get(key)

    def has(self, key: str) -> bool:
        """Kiểm tra key có trong bảng không. O(1)."""
        return key in self._store

    def delete(self, key: str) -> bool:
        """Xóa key, trả True nếu tìm thấy. O(1)."""
        if key in self._store:
            del self._store[key]
            return True
        return False

    def clear(self) -> None:
        """Xóa toàn bộ bảng. O(1)."""
        self._store.clear()

    def size(self) -> int:
        """Số phần tử hiện có. O(1)."""
        return len(self._store)

    def values(self) -> list:
        """Trả về list tất cả value. O(N)."""
        return list(self._store.values())

    def __len__(self) -> int:
        return len(self._store)

    def __repr__(self) -> str:
        return f"HashMap(size={len(self._store)})"
