# =============================================================================
# main.py — Điểm vào duy nhất của ứng dụng
#
# Cách chạy:
#   python main.py
#
# Cấu trúc dự án:
#   HospitalQueue/
#   ├── main.py               ← file này
#   ├── Data/
#   │   ├── patient.py        — kiểu dữ liệu Patient
#   │   └── dataset/          — queue.csv, history.csv, counters.txt
#   ├── DataStructures/
#   │   ├── min_heap.py       — ADT MinHeap
#   │   ├── linked_list.py    — ADT SinglyLinkedList + LinkedList
#   │   └── hash_map.py       — ADT HashMap + PatientHashMap
#   ├── Algorithm/
#   │   ├── priority_queue.py — PriorityQueue (dùng MinHeap)
#   │   ├── history.py        — History (dùng LinkedList)
#   │   └── scheduler.py      — Scheduler (điều phối nghiệp vụ)
#   └── UI/
#       └── main_console.py   — Giao diện dòng lệnh
# =============================================================================

import sys
import os

# Thêm thư mục gốc vào sys.path để các module con import lẫn nhau được
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from UI.main_console import run

if __name__ == "__main__":
    run()
