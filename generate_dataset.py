# =============================================================================
# generate_dataset.py — Tạo dữ liệu mẫu cho hệ thống
#
# Cách chạy (từ thư mục HospitalQueue/):
#     python generate_dataset.py
#     python generate_dataset.py --queue 20 --history 10 --seed 42
#
# Tùy chọn:
#     --queue   N  : số bệnh nhân trong hàng đợi (mặc định: 15)
#     --history N  : số bệnh nhân trong lịch sử  (mặc định: 8)
#     --seed    N  : hạt giống random (mặc định: 42, kết quả tái lặp được)
#     --reset      : xóa dataset cũ trước khi tạo mới
#
# Ví dụ:
#     python generate_dataset.py --queue 30 --history 15 --reset
# =============================================================================

import sys
import os
import random
import argparse
from datetime import datetime, timedelta

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from Algorithm.scheduler      import Scheduler
from Algorithm.priority_queue import PriorityQueue
from Algorithm.history        import History
from Data.patient             import Patient, SEVERITY_LABELS

# ─── Dữ liệu mẫu ─────────────────────────────────────────────────────────────

_FIRST_NAMES = [
    "Nguyễn Văn", "Trần Thị", "Lê Văn", "Phạm Thị", "Hoàng Văn",
    "Vũ Thị",     "Đặng Văn", "Bùi Thị", "Đỗ Văn",   "Hồ Thị",
    "Ngô Văn",    "Dương Thị","Lý Văn",  "Đinh Thị", "Mai Văn",
]

_LAST_NAMES = [
    "An", "Bình", "Cường", "Dung", "Em",
    "Phương", "Giang", "Hà", "Inh", "Khánh",
    "Lan", "Minh", "Nam", "Oanh", "Phúc",
    "Quỳnh", "Rồng", "Sơn", "Thảo", "Uyên",
]

_ARRIVAL_HOURS = [7, 7, 8, 8, 8, 9, 9, 10, 10, 11, 13, 14, 15, 16]


def _random_name(rng: random.Random) -> str:
    return f"{rng.choice(_FIRST_NAMES)} {rng.choice(_LAST_NAMES)}"


def _random_arrival(rng: random.Random) -> str:
    h = rng.choice(_ARRIVAL_HOURS)
    m = rng.randint(0, 59)
    return f"{h:02d}:{m:02d}"


def _random_time_called(rng: random.Random) -> str:
    """Sinh giờ gọi khám ngẫu nhiên trong khoảng 07:00–17:00."""
    total_min = rng.randint(7 * 60, 17 * 60)
    h, m = divmod(total_min, 60)
    s = rng.randint(0, 59)
    return f"{h:02d}:{m:02d}:{s:02d}"


# ─── Hàm tạo dữ liệu ─────────────────────────────────────────────────────────

def generate_queue(sched: Scheduler, n: int, rng: random.Random) -> None:
    """
    Thêm n bệnh nhân ngẫu nhiên vào hàng đợi qua Scheduler.

    Phân bố severity cố ý lệch để dataset trông thực tế hơn:
        Mức 1 (nguy kịch) : ~10%
        Mức 2 (nặng)      : ~20%
        Mức 3 (trung bình): ~35%
        Mức 4 (nhẹ)       : ~25%
        Mức 5 (rất nhẹ)   : ~10%
    """
    # Trọng số theo mức độ bệnh
    severity_weights = [10, 20, 35, 25, 10]
    severity_pool    = []
    for sev, w in enumerate(severity_weights, start=1):
        severity_pool.extend([sev] * w)

    added = 0
    for _ in range(n):
        name         = _random_name(rng)
        age          = rng.randint(1, 90)
        severity     = rng.choice(severity_pool)
        arrival_time = _random_arrival(rng)

        ok, msg, p = sched.add_patient(name, age, severity, arrival_time)
        if ok:
            added += 1
        else:
            print(f"  [WARN] Bỏ qua: {msg}")

    print(f"  ✓ Đã thêm {added}/{n} bệnh nhân vào hàng đợi.")


def generate_history(sched: Scheduler, n: int, rng: random.Random) -> None:
    """
    Thêm trực tiếp n bản ghi vào lịch sử (không qua hàng đợi).

    Mục đích: mô phỏng các bệnh nhân đã được khám trước đó.
    Dùng Patient.from_dict() để tạo dữ liệu rồi ghi thẳng vào History.
    """
    severity_weights = [10, 20, 35, 25, 10]
    severity_pool    = []
    for sev, w in enumerate(severity_weights, start=1):
        severity_pool.extend([sev] * w)

    for i in range(1, n + 1):
        pid = f"LS{i:04d}"          # prefix LS = Lịch Sử, phân biệt với BN đang chờ
        p = Patient(
            patient_id   = pid,
            name         = _random_name(rng),
            age          = rng.randint(1, 90),
            severity     = rng.choice(severity_pool),
            arrival_time = _random_arrival(rng),
            reg_order    = i,
        )
        time_called = _random_time_called(rng)
        sched._history.add_record(p, time_called)

    sched._history.save_to_file()
    print(f"  ✓ Đã thêm {n} bản ghi vào lịch sử.")


# ─── Xóa dataset cũ ──────────────────────────────────────────────────────────

def reset_dataset() -> None:
    """Xóa toàn bộ file trong Data/dataset/ để bắt đầu lại từ đầu."""
    dataset_dir = os.path.join(ROOT, "Data", "dataset")
    if not os.path.exists(dataset_dir):
        return
    deleted = 0
    for fname in ["queue.csv", "history.csv", "counters.txt"]:
        fpath = os.path.join(dataset_dir, fname)
        if os.path.exists(fpath):
            os.remove(fpath)
            deleted += 1
    print(f"  ✓ Đã xóa {deleted} file cũ trong Data/dataset/.")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Tạo dữ liệu mẫu cho hệ thống Quản lý Bệnh viện",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--queue",   type=int, default=15,
                        metavar="N", help="Số bệnh nhân trong hàng đợi (mặc định: 15)")
    parser.add_argument("--history", type=int, default=8,
                        metavar="N", help="Số bệnh nhân trong lịch sử  (mặc định: 8)")
    parser.add_argument("--seed",    type=int, default=42,
                        metavar="N", help="Hạt giống random              (mặc định: 42)")
    parser.add_argument("--reset",   action="store_true",
                        help="Xóa dataset cũ trước khi tạo mới")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    print("=" * 56)
    print("  GENERATE DATASET — Hệ thống Quản lý Bệnh viện")
    print("=" * 56)
    print(f"  Seed     : {args.seed}")
    print(f"  Queue    : {args.queue} bệnh nhân")
    print(f"  History  : {args.history} bản ghi")
    print()

    if args.reset:
        print("[1/3] Xóa dataset cũ...")
        reset_dataset()
    else:
        print("[1/3] Giữ nguyên dataset cũ (dùng --reset để xóa).")

    print(f"\n[2/3] Tạo {args.queue} bệnh nhân trong hàng đợi...")
    sched = Scheduler()
    generate_queue(sched, args.queue, rng)

    print(f"\n[3/3] Tạo {args.history} bản ghi lịch sử...")
    generate_history(sched, args.history, rng)

    # ─── Tóm tắt ─────────────────────────────────────────────────────────────
    print("\n" + "─" * 56)
    print("  Tóm tắt dataset:")
    print(f"    Đang chờ : {sched.count_waiting()}")
    print(f"    Lịch sử  : {sched.count_examined()}")
    counts = sched.count_by_severity()
    for sev in range(1, 6):
        label = SEVERITY_LABELS[sev]
        bar   = "█" * counts[sev]
        print(f"    Mức {sev} {label:<12}: {counts[sev]:>3}  {bar}")
    print("─" * 56)
    print("  Chạy chương trình chính: python main.py")
    print("=" * 56)


if __name__ == "__main__":
    main()
