import unittest

from hexgrid import HexGrid

class TestHexGrid(unittest.TestCase):
    def setUp(self):
        self.g = HexGrid(7, list)

    def test_sidelen(self):
        self.assertEqual(13, len(self.g.leftedges))
        self.assertEqual(13, len(self.g.uredges))
        self.assertEqual(13, len(self.g.lredges))

    def test_traversal_len(self):
        lengths = [7,8,9,10,11,12,13,12,11,10,9,8,7]

        for i in range(13):
            self.assertEqual(lengths[i],
                    len(list(self.g.traverse_l2r(i))))
            self.assertEqual(lengths[i],
                    len(list(self.g.traverse_lr2ul(i))))
            self.assertEqual(lengths[i],
                    len(list(self.g.traverse_ur2ll(i))))

    def _fill_by_row(self):
        for i in range(13):
            for cell in self.g.traverse_l2r(i):
                cell.append(i)
    def _fill_by_diag(self):
        for i in range(13):
            for cell in self.g.traverse_ur2ll(i):
                cell.append(i)

    def test_row_storage(self):
        # Fill each row with its index
        self._fill_by_row()

        # Now traverse ur2ll and make sure the order goes descending from
        # 12 to 0
        for i in range(7):
            for cell, expected in zip(self.g.traverse_ur2ll(i),
                    range(12,-1,-1)):
                self.assertEqual([expected], cell)

        # From 7-12 the starting number is reduced
        for i in range(7,13):
            for cell, expected in zip(self.g.traverse_ur2ll(i),
                    range(12-(i-6), -1, -1)):
                self.assertEqual([expected], cell)

        # Now traverse lr2ul and make sure the values increase. For the
        # first 7 we expect it to start not at 0
        for i in range(0,7):
            for cell, expected in zip(self.g.traverse_lr2ul(i),
                    range(6-i, 13)):
                self.assertEqual([expected], cell)

        for i in range(7,13):
            for cell, expected in zip(self.g.traverse_lr2ul(i),
                    range(0, 13)):
                self.assertEqual([expected], cell)

    def test_total_cells(self):
        """Tests that exactly the expected number of cells exist and are
        reachable with the three directions of traversal"""
        all_items = set()
        for i in range(13):
            for cell in self.g.traverse_l2r(i):
                all_items.add(id(cell))
        self.assertEqual(127, len(all_items))

        all_items = set()
        for i in range(13):
            for cell in self.g.traverse_lr2ul(i):
                all_items.add(id(cell))
        self.assertEqual(127, len(all_items))

        all_items = set()
        for i in range(13):
            for cell in self.g.traverse_ur2ll(i):
                all_items.add(id(cell))

        self.assertEqual(127, len(all_items))

    def _get_all_cells(self):
        all_cells = []
        for cell in self.g.leftedges:
            while cell is not None:
                all_cells.append(cell)
                cell = cell.right
        return all_cells

    def test_node_single_links(self):
        """Test and make sure each of the 6 links, if they go to a node,
        the appropriate link from that node go back.

        """
        # First get us a list of every cell object (not cell value)
        all_cells = self._get_all_cells()

        self._fill_by_row() # To help in debugging

        # Now do the test
        for cell in all_cells:
            if cell.right:
                self.assertIs(cell, cell.right.left)
            if cell.left:
                self.assertIs(cell, cell.left.right)
            if cell.ul:
                self.assertIs(cell, cell.ul.lr)
            if cell.ur:
                self.assertIs(cell, cell.ur.ll)
            if cell.lr:
                self.assertIs(cell, cell.lr.ul)
            if cell.ll:
                self.assertIs(cell, cell.ll.ur)

    def test_node_link_circle(self):
        self._fill_by_row() # To help in debugging
        self._fill_by_diag()
        for cell in self._get_all_cells():

            # ur → lr → left
            if cell.ur and cell.ur.lr:
                self.assertIs(cell, cell.ur.lr.left)

            # right → ll → ul
            if cell.right and cell.right.ll:
                self.assertIs(cell, cell.right.ll.ul)

            # ll → ul → right
            if cell.ll and cell.ll.ul:
                self.assertIs(cell, cell.ll.ul.right)

            # left → ur → lr
            if cell.left and cell.left.ur:
                self.assertIs(cell, cell.left.ur.lr)

            # ul → right → ll
            if cell.ul and cell.ul.right:
                self.assertIs(cell, cell.ul.right.ll)

            # Now for counterclockwise circles

            # right → ul → ll
            if cell.right and cell.right.ul:
                self.assertIs(cell, cell.right.ul.ll)

            # ur → left → lr
            if cell.ur and cell.ur.left:
                self.assertIs(cell, cell.ur.left.lr)

            # ul → ll → right
            if cell.ul and cell.ul.ll:
                self.assertIs(cell, cell.ul.ll.right)

            # left → lr → ur
            if cell.left and cell.left.lr:
                self.assertIs(cell, cell.left.lr.ur)

            # ll → right → ul
            if cell.ll and cell.ll.right:
                self.assertIs(cell, cell.ll.right.ul)

            # lr → ur → left
            if cell.lr and cell.lr.ur:
                self.assertIs(cell, cell.lr.ur.left)

if __name__ == "__main__":
    unittest.main()
