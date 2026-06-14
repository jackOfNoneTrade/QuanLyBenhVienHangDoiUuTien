import time
import random
from Data.patient import Patient
from DataStructures.min_heap import MinHeap

# --- CẤU TRÚC 1: BINARY HEAP (Dùng class của nhóm) ---
def test_binary_heap(patients):
    heap = MinHeap()
    # Đo Enqueue
    for p in patients:
        heap.insert(p)
    # Đo Dequeue
    while not heap.is_empty():
        heap.extract_min()

# --- CẤU TRÚC 2: UNSORTED LIST (Dùng list Python thuần) ---
def test_unsorted_list(patients):
    lst = []
    # Enqueue: O(1)
    for p in patients:
        lst.append(p)
    # Dequeue: O(N) vì phải tìm min rồi xóa
    while lst:
        m = min(lst) # Tìm min dựa trên __lt__ của Patient
        lst.remove(m)

# --- CẤU TRÚC 3: SORTED LIST (Dùng list Python giữ thứ tự) ---
def test_sorted_list(patients):
    lst = []
    # Enqueue: O(N) vì phải tìm vị trí chèn và dịch hàng
    for p in patients:
        # Tìm vị trí chèn để list luôn tăng dần
        inserted = False
        for i in range(len(lst)):
            if p < lst[i]:
                lst.insert(i, p)
                inserted = True
                break
        if not inserted:
            lst.append(p)
    # Dequeue: O(1) hoặc O(N) tùy đầu xóa. 
    # Nếu pop(0) là O(N). Để công bằng với Heap, ta dùng pop(0)
    while lst:
        lst.pop(0)

def generate_patients(n):
    patients = []
    for i in range(n):
        p = Patient(
            patient_id=f"BN{i:04d}",
            name=f"Patient_{i}",
            age=random.randint(1, 90),
            severity=random.randint(1, 5),
            arrival_time=f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
            reg_order=i # Đảm bảo duy nhất để không bị lỗi so sánh
        )
        patients.append(p)
    return patients

def measure(fn, patients):
    # Chạy 3 lần lấy trung bình để tránh nhiễu (warm-up effect)
    times = []
    for _ in range(3):
        start = time.perf_counter()
        fn(patients)
        end = time.perf_counter()
        times.append((end - start) * 1000) # đổi sang ms
    return sum(times) / 3

if __name__ == "__main__":
    N_values = [500, 1000, 2000, 5000, 10000]
    
    print(f"{'N':>6} | {'Binary Heap (ms)':>18} | {'Unsorted List (ms)':>18} | {'Sorted List (ms)':>18}")
    print("-" * 70)
    
    for n in N_values:
        data = generate_patients(n)
        
        t_heap = measure(test_binary_heap, data)
        t_unsorted = measure(test_unsorted_list, data)
        t_sorted = measure(test_sorted_list, data)
        
        print(f"{n:6d} | {t_heap:18.2f} | {t_unsorted:18.2f} | {t_sorted:18.2f}")

    print("\nLưu ý: Kết quả có thể thay đổi tùy cấu hình máy tính.")