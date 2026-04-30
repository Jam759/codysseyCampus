class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.size = 0

    def insert(self, data, position=None):
        new_node = Node(data)

        if position is None:
            position = self.size

        if position < 0 or position > self.size:
            raise IndexError('insert position is out of range')

        if position == 0:
            new_node.next = self.head
            self.head = new_node
            self.size += 1
            return

        previous_node = self.head

        for _ in range(position - 1):
            previous_node = previous_node.next

        new_node.next = previous_node.next
        previous_node.next = new_node
        self.size += 1

    def delete(self, data):
        current_node = self.head
        previous_node = None

        while current_node is not None:
            if current_node.data == data:
                if previous_node is None:
                    self.head = current_node.next
                else:
                    previous_node.next = current_node.next

                self.size -= 1
                return True

            previous_node = current_node
            current_node = current_node.next

        return False

    def get_list(self):
        items = []
        current_node = self.head

        while current_node is not None:
            items.append(current_node.data)
            current_node = current_node.next

        return items


class CircularList:
    def __init__(self):
        self.head = None
        self.current = None
        self.size = 0

    def insert(self, data, position=None):
        new_node = Node(data)

        if position is None:
            position = self.size

        if position < 0 or position > self.size:
            raise IndexError('insert position is out of range')

        if self.head is None:
            new_node.next = new_node
            self.head = new_node
            self.current = new_node
            self.size += 1
            return

        if position == 0:
            tail_node = self._get_tail()
            new_node.next = self.head
            tail_node.next = new_node
            self.head = new_node
            self.size += 1
            return

        previous_node = self.head

        for _ in range(position - 1):
            previous_node = previous_node.next

        new_node.next = previous_node.next
        previous_node.next = new_node
        self.size += 1

    def delete(self, data):
        if self.head is None:
            return False

        current_node = self.head
        previous_node = self._get_tail()

        for _ in range(self.size):
            if current_node.data == data:
                if self.size == 1:
                    self.head = None
                    self.current = None
                else:
                    previous_node.next = current_node.next

                    if current_node == self.head:
                        self.head = current_node.next

                    if current_node == self.current:
                        self.current = current_node.next

                self.size -= 1
                return True

            previous_node = current_node
            current_node = current_node.next

        return False

    def get_next(self):
        if self.current is None:
            return None

        data = self.current.data
        self.current = self.current.next
        return data

    def search(self, data):
        if self.head is None:
            return -1

        current_node = self.head

        for index in range(self.size):
            if current_node.data == data:
                return index

            current_node = current_node.next

        return -1

    def get_list(self):
        items = []

        if self.head is None:
            return items

        current_node = self.head

        for _ in range(self.size):
            items.append(current_node.data)
            current_node = current_node.next

        return items

    def _get_tail(self):
        current_node = self.head

        for _ in range(self.size - 1):
            current_node = current_node.next

        return current_node


def print_music_list(title, music_list):
    print(title)

    for index, music in enumerate(music_list, start=1):
        print(f'{index}. {music}')

    print()


def run_linked_list_example():
    linkedlist = LinkedList()

    linkedlist.insert('Ditto')
    linkedlist.insert('Love wins all')
    linkedlist.insert('Supernova')
    linkedlist.insert('Hype Boy', 1)
    linkedlist.insert('Seven', 0)
    linkedlist.delete('Love wins all')

    print_music_list('[LinkedList music]', linkedlist.get_list())


def run_circular_list_example():
    circularlist = CircularList()

    circularlist.insert('Dynamite')
    circularlist.insert('ETA')
    circularlist.insert('Magnetic')
    circularlist.insert('Drama', 2)
    circularlist.delete('ETA')

    print_music_list('[CircularList music]', circularlist.get_list())

    print('Search Magnetic :', circularlist.search('Magnetic'))
    print('Play order')

    for _ in range(5):
        print('-', circularlist.get_next())


def main():
    run_linked_list_example()
    run_circular_list_example()


if __name__ == '__main__':
    main()
