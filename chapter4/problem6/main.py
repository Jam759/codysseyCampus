class Stack:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.items = []

    def push(self, item):
        if len(self.items) >= self.max_size:
            print('스택이 가득 찼습니다. 더 이상 추가할 수 없습니다.')
            return

        self.items.append(item)
        print(item, '추가 완료')

    def pop(self):
        if self.empty():
            print('스택이 비어 있습니다. 가져올 내용이 없습니다.')
            return None

        item = self.items.pop()
        print(item, '가져오기 완료')
        return item

    def empty(self):
        return len(self.items) == 0

    def peek(self):
        if self.empty():
            print('스택이 비어 있습니다. 확인할 내용이 없습니다.')
            return None

        return self.items[-1]

    def show_stack(self):
        print()
        print('현재 스택 상태')
        print('--------------------')

        if self.empty():
            print('|      비어 있음      |')
        else:
            for index in range(len(self.items) - 1, -1, -1):
                if index == len(self.items) - 1:
                    print('|', self.items[index], '<- top')
                else:
                    print('|', self.items[index])

        print('--------------------')
        print('현재 개수:', len(self.items), '/', self.max_size)
        print()


def main():
    stack = Stack()

    print('스택에 데이터 추가')
    for number in range(1, 11):
        stack.push('data_' + str(number))

    stack.show_stack()

    print('스택이 가득 찬 상태에서 추가 시도')
    stack.push('data_11')

    print()
    print('peek() 실행')
    top_item = stack.peek()
    print('마지막 내용:', top_item)

    stack.show_stack()

    print('pop() 실행')
    for _ in range(3):
        stack.pop()

    stack.show_stack()

    print('empty() 실행')
    print('스택이 비어 있는가:', stack.empty())

    print()
    print('모든 데이터 꺼내기')
    while not stack.empty():
        stack.pop()

    stack.show_stack()

    print('비어 있는 상태에서 pop() 실행')
    stack.pop()

    print()
    print('비어 있는 상태에서 peek() 실행')
    stack.peek()


if __name__ == '__main__':
    main()