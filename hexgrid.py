

class HexGrid:
    """This class represents a hexagonal grid. The hexagons are themselves
    arranged in a hexagon with the given side length.
    
    """

    def __init__(self, sidelen, defaultvaluegenerator):
        self.sidelen = sidelen
        self.defaultvaluegenerator = defaultvaluegenerator

        # The structure is a grid of linked cells. Each cell has 6 links, one
        # for each of its neighbors. We hold in this object three lists, one
        # for the left edges, one for the upper right edges, and one for the
        # lower right edges. Order goes clockwise.
        self.leftedges = []
        self.uredges = []
        self.lredges = []

        # Create the top row
        row = []
        lastcell = None
        for _ in range(sidelen):
            newcell = Cell(defaultvaluegenerator())
            row.append(newcell)
            if lastcell:
                lastcell.right = newcell
                newcell.left = lastcell
            lastcell = newcell

        self.uredges.extend(row)
        self.leftedges.append(row[0])

        for _ in range(self.sidelen-1):
            row = self._newrow_expand(row)

        self.lredges.append(row[-1])
        
        for _ in range(self.sidelen-1):
            row = self._newrow_contract(row)
        self.lredges.extend(reversed(row[:-1]))

        self.leftedges.reverse()

    def traverse_l2r(self, index):
        """Returns an iterator over cell values starting at a cell on one of
        the left edges and traversing horizontally to the right.

        """
        cell = self.leftedges[index]
        while cell is not None:
            yield cell.value
            cell = cell.right

    def traverse_ur2ll(self, index):
        """Returns an iterator over cell values starting at a cell on one of
        the upper-right edges and traversing diagonally to the lower-left.

        """
        cell = self.uredges[index]
        while cell is not None:
            yield cell.value
            cell = cell.ll

    def traverse_lr2ul(self, index):
        """Returns an iterator over cell values starting at a cell on one of
        the lower-right edges and traversing diagonally to the upper-left.

        """
        cell = self.lredges[index]
        while cell is not None:
            yield cell.value
            cell = cell.ul

    def _newrow_expand(self, lastrow):
        """Add a new row of one length longer than the last one"""
        newrow = []

        # Create the first node in the new row
        newrow.append(Cell(self.defaultvaluegenerator()))
        lastrow[0].ll = newrow[0]
        newrow[0].ur = lastrow[0]

        # Create all the inner nodes in the new row and connect them to their
        # upper right and upper left neighbors
        for ulneighbor, urneighbor in zip(lastrow[:-1], lastrow[1:]):
            newcell = Cell(self.defaultvaluegenerator())
            newcell.ul = ulneighbor
            ulneighbor.lr = newcell
            newcell.ur = urneighbor
            urneighbor.ll = newcell
            newrow.append(newcell)

        # Now create the last node in the row
        newrow.append(Cell(self.defaultvaluegenerator()))
        lastrow[-1].lr = newrow[-1]
        newrow[-1].ul = lastrow[-1]

        # Now go and link each node in the row to each other
        for left, right in zip(newrow[:-1], newrow[1:]):
            left.right = right
            right.left = left

        self.leftedges.append(newrow[0])
        self.uredges.append(newrow[-1])

        return newrow

    def _newrow_contract(self, lastrow):
        """Add a new row one length shorter than the last one"""
        newrow = []

        # Create all the inner nodes in the new row and connect them to their
        # upper right and upper left neighbors
        for ulneighbor, urneighbor in zip(lastrow[:-1], lastrow[1:]):
            newcell = Cell(self.defaultvaluegenerator())
            newcell.ul = ulneighbor
            ulneighbor.lr = newcell
            newcell.ur = urneighbor
            urneighbor.ll = newcell
            newrow.append(newcell)

        # Now go and link each node in the row to each other
        for left, right in zip(newrow[:-1], newrow[1:]):
            left.right = right
            right.left = left

        self.leftedges.append(newrow[0])
        self.lredges.append(newrow[-1])

        return newrow



class Cell:
    """A single cell in the grid. Holds a value and 6 links.

    """
    __slots__ = ("value", "left", "ul", "ur", "right", "lr", "ll")
    def __init__(self, value):
        self.value = value

        self.left = None
        self.ul = None
        self.ur = None
        self.right = None
        self.lr = None
        self.ll = None

    def __repr__(self):
        return "<Cell: {0!r}>".format(self.value)
