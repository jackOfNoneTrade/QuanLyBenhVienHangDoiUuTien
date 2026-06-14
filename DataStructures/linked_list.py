# =============================================================================
# Data/linked_list.py
# ADT: Danh sách liên kết đơn (Singly Linked List)
#
# Vai trò trong hệ thống bệnh viện:
#   Lưu lịch sử bệnh nhân đã khám theo thứ tự thời gian.
#   Mỗi khi bệnh nhân được gọi khám (pop từ heap), đối tượng Patient đó
#   được append vào cuối danh sách → ghi nhận trình tự khám thực tế.
#
# Độ phức tạp các thao tác chính:
#   append(data)   O(1)  — nhờ tail
#   prepend(data)  O(1)  — nhờ head
#   pop_front()    O(1)  — nhờ head  (list.pop(0) của Python là O(N))
#   find(id)       O(N)  — phải duyệt tuần tự
#   __len__        O(1)  — duy trì biến _size
# =============================================================================


class Node:
    """
    Một nút trong danh sách liên kết đơn.

    Thuộc tính:
        data : Dữ liệu lưu trữ (trong hệ thống này là đối tượng Patient).
        next : Con trỏ trỏ đến nút TIẾP THEO; là None nếu đây là nút cuối.
    """

    # __slots__ tối ưu bộ nhớ: Python không tạo __dict__ cho mỗi Node
    __slots__ = ('data', 'next')

    def __init__(self, data):
        self.data = data   # payload — dữ liệu thực sự cần lưu
        self.next = None   # chưa liên kết với nút nào; gán sau khi chèn

    def __repr__(self):
        return f"Node({self.data!r})"


# =============================================================================

class SinglyLinkedList:
    """
    Danh sách liên kết đơn với con trỏ head và tail.

    Thuộc tính nội bộ:
        _head (Node|None) : Nút đầu tiên — điểm vào của danh sách.
        _tail (Node|None) : Nút cuối cùng — cho phép append O(1).
        _size (int)       : Số phần tử; giúp __len__ trả về O(1).

    Khi danh sách rỗng: _head = _tail = None, _size = 0.
    Khi có đúng 1 phần tử: _head và _tail cùng trỏ đến nút duy nhất đó.
    """

    def __init__(self):
        self._head: Node | None = None
        self._tail: Node | None = None
        self._size: int = 0

    # =========================================================================
    # THÊM PHẦN TỬ
    # =========================================================================

    def append(self, data) -> None:
        """
        Thêm phần tử vào CUỐI danh sách.   O(1).

       nhờ _tail ta biết ngay nút cuối, không cần duyệt:

          Bước 1: Tạo nút mới.
          Bước 2: Nối tail hiện tại sang nút mới  (tail.next = new_node).
          Bước 3: Cập nhật tail trỏ vào nút mới   (_tail = new_node).

       
        """
        new_node = Node(data)

        if self._tail is None:
            # Danh sách đang rỗng → nút mới vừa là head vừa là tail
            self._head = new_node
            self._tail = new_node
        else:
            # Nối nút mới vào sau tail, rồi dịch tail sang phải
            self._tail.next = new_node    # bước 2
            self._tail = new_node         # bước 3

        self._size += 1

    def prepend(self, data) -> None:
        """
        Thêm phần tử vào ĐẦU danh sách.   O(1).

        Cơ chế:
          Bước 1: Tạo nút mới.
          Bước 2: new_node.next trỏ vào head hiện tại.
          Bước 3: Cập nhật head = new_node.

        """
        new_node = Node(data)

        if self._head is None:
            self._head = new_node
            self._tail = new_node
        else:
            new_node.next = self._head   # bước 2
            self._head = new_node         # bước 3

        self._size += 1

    # =========================================================================
    # XOÁ PHẦN TỬ
    # =========================================================================

    def pop_front(self):
        """
        Xoá và trả về phần tử ở ĐẦU danh sách.   Độ phức tạp: O(1).

        Ném IndexError nếu danh sách rỗng.

        Cơ chế — chỉ cập nhật con trỏ head, không dịch chuyển dữ liệu:
          Bước 1: Lưu data của head.
          Bước 2: _head = _head.next  (bỏ nút đầu ra khỏi chuỗi).
          Bước 3: Nếu head mới là None → danh sách vừa rỗng → _tail = None.

        """
        if self._head is None:
            raise IndexError("pop_front() trên danh sách rỗng.")

        data = self._head.data        # bước 1: lưu lại giá trị cần trả về
        self._head = self._head.next  # bước 2: bỏ qua nút đầu

        if self._head is None:
            # Vừa xoá phần tử CUỐI CÙNG → tail cũng trỏ về None
            self._tail = None

        self._size -= 1
        return data

    def remove(self, data) -> bool:
        """
        Xoá lần xuất hiện ĐẦU TIÊN của data.   Độ phức tạp: O(N).

        Dùng __eq__ của data để so sánh.
        Trả về True nếu tìm thấy và đã xoá, False nếu không có.

        Cơ chế — dùng con trỏ prev để "nối tắt" qua nút cần xoá:
        """
        prev = None
        curr = self._head

        # ── Duyệt linked list: while node is not None ──
        while curr is not None:
            if curr.data == data:
                if prev is None:
                    # Xoá nút đầu → cập nhật head
                    self._head = curr.next
                else:
                    # Nối prev thẳng sang nút sau curr → bỏ qua curr
                    prev.next = curr.next

                if curr.next is None:
                    # Xoá nút cuối → cập nhật tail
                    self._tail = prev

                self._size -= 1
                return True

            prev = curr
            curr = curr.next   # ← bước tiến: không dùng index, dùng con trỏ

        return False   # không tìm thấy

    # TRUY VẤN (không thay đổi cấu trúc)

    def peek_front(self):
        """Đọc phần tử đầu mà KHÔNG xoá.   O(1)."""
        if self._head is None:
            raise IndexError("peek_front() trên danh sách rỗng.")
        return self._head.data

    def peek_back(self):
        """Đọc phần tử cuối mà KHÔNG xoá.   O(1) nhờ _tail."""
        if self._tail is None:
            raise IndexError("peek_back() trên danh sách rỗng.")
        return self._tail.data

    def find(self, patient_id: str):
        """
        Tìm Patient theo patient_id.   Độ phức tạp: O(N).

        Phải duyệt tuần tự từ đầu — linked list không có random access.
        Đây là điểm yếu so với HashMap (O(1)); dùng HashMap khi cần tra
        cứu theo ID thường xuyên.

        Trả về: đối tượng Patient nếu tìm thấy, None nếu không có.
        """
        # ── Duyệt: while node is not None, tiến bằng curr = curr.next ──
        curr = self._head
        while curr is not None:
            if hasattr(curr.data, 'patient_id') and curr.data.patient_id == patient_id:
                return curr.data
            curr = curr.next   # truy cập phần tử tiếp theo qua con trỏ, không phải index
        return None

    def to_list(self) -> list:
        """
        Chuyển toàn bộ linked list sang list Python.   O(N).
        Hữu ích khi cần xuất CSV hoặc hiển thị lịch sử khám.
        """
        result = []
        curr = self._head
        while curr is not None:   # ── duyệt: while node is not None ──
            result.append(curr.data)
            curr = curr.next
        return result

    # MAGIC METHOD

    def __len__(self) -> int:
        """Số phần tử.   O(1) nhờ biến _size được cập nhật liên tục."""
        return self._size

    def __bool__(self) -> bool:
        """True nếu danh sách không rỗng."""
        return self._size > 0

    def __iter__(self):
        """
        Cho phép dùng vòng for.   O(N) tổng cộng.

        Bên trong generator: duyệt bằng while curr is not None,
        yield từng curr.data — không dùng index số nguyên.

            for patient in history:
                print(patient)
        """
        curr = self._head
        while curr is not None:     # ── duyệt: while node is not None ──
            yield curr.data
            curr = curr.next        # tiến sang nút tiếp theo qua con trỏ

    def __contains__(self, data) -> bool:
        """Toán tử `in`.   O(N)."""
        for item in self:
            if item == data:
                return True
        return False

    def __str__(self) -> str:
        if not self._head:
            return "LinkedList: [rỗng]"
        parts = []
        curr = self._head
        while curr is not None:
            parts.append(repr(curr.data))
            curr = curr.next
        return "LinkedList: " + " → ".join(parts) + " → None"

    def __repr__(self) -> str:
        return f"SinglyLinkedList(size={self._size})"

# KIỂM TRA THỦ CÔNG
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from patient import Patient

    print("=" * 60)
    print("  KIỂM TRA SinglyLinkedList")
    print("=" * 60)

    history = SinglyLinkedList()
    print(f"\n[1] Khởi tạo: {history}")
    print(f"    Rỗng? {not history}  |  len={len(history)}")
    assert len(history) == 0

    # ── Tạo dữ liệu mẫu ──
    p1 = Patient("BN0001", "Nguyen Van An",  45, 1, "08:00", reg_order=1)
    p2 = Patient("BN0002", "Tran Thi Binh",  30, 2, "08:15", reg_order=2)
    p3 = Patient("BN0003", "Le Van Cuong",   60, 1, "08:30", reg_order=3)
    p4 = Patient("BN0004", "Pham Thi Dung",  25, 3, "09:00", reg_order=4)

    # ── append: O(1) nhờ tail ──
    print("\n[2] append() — O(1) nhờ con trỏ tail:")
    for p in [p1, p2, p3]:
        history.append(p)
        print(f"    append({p.patient_id})  →  head={history._head.data.patient_id}"
              f"  tail={history._tail.data.patient_id}  len={len(history)}")

    print(f"\n    {history}")
    assert len(history) == 3
    assert history.peek_front().patient_id == "BN0001"
    assert history.peek_back().patient_id  == "BN0003"

    # ── prepend: O(1) nhờ head ──
    print("\n[3] prepend() — O(1) nhờ con trỏ head:")
    history.prepend(p4)
    print(f"    prepend({p4.patient_id})  →  {history}")
    assert history.peek_front().patient_id == "BN0004"
    assert len(history) == 4

    # ── duyệt: while node is not None ──
    print("\n[4] Duyệt danh sách (while curr is not None / for ... in):")
    for p in history:
        print(f"    {p}")

    # ── find: O(N), dùng while curr is not None ──
    print("\n[5] find() — O(N), duyệt tuần tự, không dùng index:")
    found = history.find("BN0002")
    print(f"    find('BN0002') → {found}")
    print(f"    find('BN9999') → {history.find('BN9999')}")
    assert found.patient_id == "BN0002"
    assert history.find("BN9999") is None

    # ── pop_front: O(1) ──
    print("\n[6] pop_front() — O(1):")
    out = history.pop_front()
    print(f"    Lấy ra: {out.patient_id}   (kỳ vọng BN0004)")
    print(f"    Còn lại: len={len(history)}, head={history._head.data.patient_id}")
    assert out.patient_id == "BN0004"
    assert len(history) == 3

    # ── remove: O(N) ──
    print("\n[7] remove() — O(N):")
    ok = history.remove(p2)
    print(f"    remove(BN0002): {ok}   (kỳ vọng True)")
    print(f"    {history}")
    assert ok and len(history) == 2

    # ── pop_front đến khi rỗng, kiểm tra tail reset ──
    print("\n[8] Pop hết phần tử, kiểm tra head=tail=None:")
    while history:
        out = history.pop_front()
        print(f"    pop_front() → {out.patient_id}")
    print(f"    head={history._head}  tail={history._tail}  len={len(history)}")
    assert history._head is None and history._tail is None and len(history) == 0

    print("\n✓ Tất cả kiểm tra SinglyLinkedList hoàn thành.\n")

# LinkedList — alias/wrapper công khai, bổ sung các method dùng trong History

class LinkedList(SinglyLinkedList):
    """
    Lớp bổ sung trên SinglyLinkedList, cung cấp thêm interface
    mà tầng Algorithm (History) cần dùng.

    Thêm:
        size()           → O(1)
        clear()          → O(1)
        find_all(pred)   → O(N)
        get_last_n(n)    → O(N)
    """

    def size(self) -> int:
        """Số phần tử hiện có. O(1)."""
        return self._size

    def clear(self) -> None:
        """Xóa toàn bộ danh sách. O(1)."""
        self._head = None
        self._tail = None
        self._size = 0

    def find_all(self, predicate) -> list:
        """
        Trả về list tất cả phần tử thỏa mãn predicate. O(N).

        Tham số:
            predicate (callable): hàm nhận data, trả True nếu khớp.
        """
        result = []
        curr = self._head
        while curr is not None:
            if predicate(curr.data):
                result.append(curr.data)
            curr = curr.next
        return result

    def get_last_n(self, n: int) -> list:
        """
        Trả về n phần tử cuối cùng (theo thứ tự từ cũ đến mới). O(N).

        Nếu n >= size thì trả về toàn bộ danh sách.
        """
        all_items = self.to_list()
        return all_items[-n:] if n < len(all_items) else all_items
