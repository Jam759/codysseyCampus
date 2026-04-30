class TreeNode:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None


class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, data):
        new_node = TreeNode(data)

        if self.root is None:
            self.root = new_node
            return

        current_node = self.root

        while True:
            if data < current_node.data:
                if current_node.left is None:
                    current_node.left = new_node
                    return

                current_node = current_node.left
            elif data > current_node.data:
                if current_node.right is None:
                    current_node.right = new_node
                    return

                current_node = current_node.right
            else:
                return

    def find(self, data):
        current_node = self.root

        while current_node is not None:
            if data == current_node.data:
                return True

            if data < current_node.data:
                current_node = current_node.left
            else:
                current_node = current_node.right

        return False

    def delete(self, data):
        self.root, deleted = self._delete_node(self.root, data)
        return deleted

    def get_list(self):
        items = []
        self._append_in_order(self.root, items)
        return items

    def _delete_node(self, node, data):
        if node is None:
            return None, False

        if data < node.data:
            node.left, deleted = self._delete_node(node.left, data)
            return node, deleted

        if data > node.data:
            node.right, deleted = self._delete_node(node.right, data)
            return node, deleted

        if node.left is None:
            return node.right, True

        if node.right is None:
            return node.left, True

        smallest_node = self._find_smallest_node(node.right)
        node.data = smallest_node.data
        node.right, _ = self._delete_node(node.right, smallest_node.data)
        return node, True

    def _find_smallest_node(self, node):
        current_node = node

        while current_node.left is not None:
            current_node = current_node.left

        return current_node

    def _append_in_order(self, node, items):
        if node is None:
            return

        self._append_in_order(node.left, items)
        items.append(node.data)
        self._append_in_order(node.right, items)


def print_tree(title, values):
    print(title)

    for value in values:
        print('-', value)

    print()


def main():
    binarytree = BinarySearchTree()

    plants = [
        'Rose',
        'Lily',
        'Tulip',
        'Daisy',
        'Sunflower',
        'Orchid',
        'Lavender',
    ]

    for plant in plants:
        binarytree.insert(plant)

    print_tree('[Plant Binary Search Tree]', binarytree.get_list())

    print('Find Orchid :', binarytree.find('Orchid'))
    print('Find Mint   :', binarytree.find('Mint'))
    print()

    binarytree.delete('Lily')
    binarytree.delete('Rose')

    print_tree('[After Delete]', binarytree.get_list())


if __name__ == '__main__':
    main()
