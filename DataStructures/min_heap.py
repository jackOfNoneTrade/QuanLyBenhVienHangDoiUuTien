# =============================================================================
# DataStructures/min_heap.py
# ADT: Min-Heap tự cài đặt (KHÔNG dùng heapq).
#
# Đây là cấu trúc dữ liệu THUẦN TÚY — không biết "bệnh nhân" là gì.
# Chỉ yêu cầu các phần tử hỗ trợ toán tử so sánh < và ==.
#
# Độ phức tạp:
#   insert       : O(log N)  — thêm cuối rồi heapify_up
#   extract_min  : O(log N)  — lấy đỉnh rồi heapify_down
#   peek_min     : O(1)      — đỉnh heap luôn ở index 0
#   is_empty     : O(1)
#   size         : O(1)
#   find         : O(N)      — heap không hỗ trợ tìm theo giá trị tùy ý
#   delete       : O(N)      — tìm + xóa + rebuild
# =============================================================================


class MinHeap:
    """
    Min-Heap lưu trữ các phần tử tùy ý theo thứ tự tăng dần.

    Biểu diễn bằng mảng (list Python):
        Nút tại vị trí i:
            cha       = (i - 1) // 2
            con trái  = 2*i + 1
            con phải  = 2*i + 2

    Tính chất heap:
        Mọi nút cha đều nhỏ hơn hoặc bằng các con.
        → heap[0] luôn là phần tử nhỏ nhất (ưu tiên cao nhất).
    """

    def __init__(self):
        self._data = []   # mảng lưu các phần tử

    # THAO TÁC CHÍNH

    def insert(self, item):
        """
        Thêm một phần tử mới vào heap.

        Thuật toán:
            1. Thêm item vào cuối mảng
            2. Gọi _heapify_up để khôi phục tính chất heap

        Độ phức tạp: O(log N)
        """
        self._data.append(item)
        self._heapify_up(len(self._data) - 1)

    def extract_min(self):
        """
        Lấy và xóa phần tử nhỏ nhất (đỉnh heap).

        Thuật toán:
            1. Nếu rỗng → trả về None
            2. Nếu chỉ 1 phần tử → pop và trả về
            3. Lưu đỉnh heap[0]
            4. Đưa phần tử cuối lên đỉnh (heap[0] = heap.pop())
            5. Gọi _heapify_down(0) để khôi phục tính chất heap

        Lý do không xóa heap[0] trực tiếp:
            list.pop(0) tốn O(N) do phải dịch toàn bộ mảng.
            Cách này chỉ tốn O(log N).

        Độ phức tạp: O(log N)
        """
        if self.is_empty():
            return None
        if len(self._data) == 1:
            return self._data.pop()

        minimum = self._data[0]
        self._data[0] = self._data.pop()   # đưa phần tử cuối lên đỉnh
        self._heapify_down(0)
        return minimum

    def peek_min(self):
        """
        Xem phần tử nhỏ nhất mà KHÔNG xóa.
        Độ phức tạp: O(1) — đỉnh heap luôn ở _data[0].
        """
        return self._data[0] if not self.is_empty() else None

    def delete(self, predicate):
        """
        Xóa phần tử đầu tiên thỏa mãn điều kiện predicate(item) == True.

        Thuật toán:
            1. Tìm index của phần tử cần xóa → O(N)
            2. Đổi chỗ với phần tử cuối
            3. Xóa phần tử cuối (giờ là phần tử cần xóa)
            4. Sửa lại heap tại vị trí đó:
               - heapify_up   (phần tử mới có thể nhỏ hơn cha)
               - heapify_down (phần tử mới có thể lớn hơn con)

        Tham số:
            predicate (callable): hàm nhận item, trả True nếu muốn xóa

        Trả về: item đã xóa, hoặc None nếu không tìm thấy.

        Độ phức tạp: O(N)
        """
        idx = -1
        for i, item in enumerate(self._data):
            if predicate(item):
                idx = i
                break

        if idx == -1:
            return None

        removed  = self._data[idx]
        last_idx = len(self._data) - 1

        if idx == last_idx:
            self._data.pop()
        else:
            self._data[idx] = self._data.pop()
            self._heapify_up(idx)
            self._heapify_down(idx)

        return removed

    def find(self, predicate):
        """
        Tìm phần tử đầu tiên thỏa mãn điều kiện (không xóa).
        Độ phức tạp: O(N)

        Trả về: item tìm thấy, hoặc None.
        """
        for item in self._data:
            if predicate(item):
                return item
        return None

    def find_all(self, predicate):
        """
        Tìm tất cả phần tử thỏa mãn điều kiện.
        Độ phức tạp: O(N)

        Trả về: list các item thỏa mãn.
        """
        return [item for item in self._data if predicate(item)]

    def to_sorted_list(self):
        """
        Trả về bản sao đã sắp xếp của tất cả phần tử.
        KHÔNG thay đổi heap gốc.
        Độ phức tạp: O(N log N)
        """
        return sorted(self._data)

    def is_empty(self):
        """Kiểm tra heap có rỗng không. O(1)"""
        return len(self._data) == 0

    def size(self):
        """Số phần tử hiện có. O(1)"""
        return len(self._data)

    def clear(self):
        """Xóa toàn bộ heap."""
        self._data = []

    def get_raw(self):
        """
        Trả về tham chiếu trực tiếp đến mảng nội bộ.
        Dùng để đọc dữ liệu (ghi file, thống kê) — KHÔNG dùng để sửa.
        """
        return self._data

    # HÀM NỘI BỘ 

    def _heapify_up(self, i):
        """
        Đẩy phần tử tại vị trí i lên đúng chỗ.

        Pseudocode:
            parent ← (i - 1) / 2
            nếu i > 0 VÀ data[i] < data[parent]:
                đổi chỗ data[i] và data[parent]
                _heapify_up(parent)

        Độ phức tạp: O(log N)
        """
        parent = (i - 1) // 2
        if i > 0 and self._data[i] < self._data[parent]:
            self._data[i], self._data[parent] = self._data[parent], self._data[i]
            self._heapify_up(parent)

    def _heapify_down(self, i):
        """
        Đẩy phần tử tại vị trí i xuống đúng chỗ.

        Pseudocode:
            smallest ← i
            left  ← 2i + 1 ;  right ← 2i + 2
            nếu left < N  VÀ data[left]  < data[smallest]: smallest ← left
            nếu right < N VÀ data[right] < data[smallest]: smallest ← right
            nếu smallest ≠ i:
                đổi chỗ data[i] và data[smallest]
                _heapify_down(smallest)

        Độ phức tạp: O(log N)
        """
        smallest = i
        left     = 2 * i + 1
        right    = 2 * i + 2
        n        = len(self._data)

        if left < n and self._data[left] < self._data[smallest]:
            smallest = left
        if right < n and self._data[right] < self._data[smallest]:
            smallest = right

        if smallest != i:
            self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
            self._heapify_down(smallest)

# KIỂM TRA THỦ CÔNG
if __name__ == "__main__":
    print("=== Test MinHeap ===\n")

    h = MinHeap()

    print("TEST 1 — insert và extract_min với số nguyên:")
    for x in [5, 3, 8, 1, 4, 2, 7]:
        h.insert(x)
    result = []
    while not h.is_empty():
        result.append(h.extract_min())
    print(f"  Kết quả  : {result}")
    print(f"  Kỳ vọng  : [1, 2, 3, 4, 5, 7, 8]")

    print("\nTEST 2 — peek_min không xóa phần tử:")
    h2 = MinHeap()
    for x in [9, 2, 6]:
        h2.insert(x)
    print(f"  peek_min : {h2.peek_min()} → Kỳ vọng: 2")
    print(f"  size sau  : {h2.size()} → Kỳ vọng: 3")

    print("\nTEST 3 — delete theo predicate:")
    h3 = MinHeap()
    for x in [4, 1, 6, 3, 8]:
        h3.insert(x)
    removed = h3.delete(lambda x: x == 6)
    print(f"  Xóa 6: {removed} → Kỳ vọng: 6")
    print(f"  Còn lại (sorted): {h3.to_sorted_list()} → Kỳ vọng: [1, 3, 4, 8]")

    print("\nTEST 4 — heap rỗng:")
    empty = MinHeap()
    print(f"  is_empty     : {empty.is_empty()} → Kỳ vọng: True")
    print(f"  extract_min  : {empty.extract_min()} → Kỳ vọng: None")
    print(f"  peek_min     : {empty.peek_min()} → Kỳ vọng: None")

    print("\n✓ Tất cả test MinHeap hoàn thành.")
