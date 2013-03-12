#!/usr/bin/env python3

import string
import time

from IPython import embed

from nfsm import NFSM
from hexgrid import HexGrid

# clockwise starting at the bottom of the lower left edge
definitions = [
        ".(C|HH)*",
        "R*D*M*",
        "N.*X.X.X.*E",
        "(RR|HHH)*.?",
        "([^X]|XCC)*",
        "(...?)\\1*",
        "[^C]*[^R]*III.*",
        "C*MC(CCC|MM)*",
        ".*",
        "(O|RHH|MM)*",
        "F.*[AO].*[AO].*",
        "(DI|NS|TH|OM)*",
        ".*H.*H.*",
        "(ND|ET|IN)[^X]*",
        "[CHMNOR]*I[CHMNOR]*",
        "P+(..)\\1.*",
        "(E|CR|MN)*",
        "([^MC]|MM|CC)*",
        "[AM]*CM(RC)*R?",
        ".*",
        ".*PRR.*DDC.*",
        "(HHX|[^HX])*",
        "([^EMC]|EM)*",
        ".*OXR.*",
        ".*LR.*RL.*",
        ".*SE.*UE.*",
        "(S|MM|HHH)*",
        "[^M]*M[^M]*",
        "(RX|[^R])*",
        "[CEIMU]*OH[AEMOR]*",
        ".*(.)C\\1X\\1.*",
        "[^C]*MMM[^C]*",
        ".*(IN|SE|HI)",
        ".*(.)(.)(.)(.)\\4\\3\\2\\1.*",
        ".*XHCR.*X.*",
        ".*DD.*CCM.*",
        ".*XEXM*",
        "[CR]*",
        ".*G.*V.*H.*",
        ]

def main():

    grid = HexGrid(7, lambda: set(string.ascii_uppercase))

    regexes = []

    print("Compiling regex objects...")
    for i, regexstr in enumerate(definitions[:13]):
        print("{0:25}".format(regexstr), end="")
        cells = list(grid.traverse_l2r(i))
        regex = NFSM(regexstr, len(cells), string.ascii_uppercase)
        regexes.append((regexstr, regex, cells))
        print("  ...done")
    for i, regexstr in enumerate(definitions[13:26]):
        print("{0:25}".format(regexstr), end="")
        cells = list(grid.traverse_ur2ll(i))
        regex = NFSM(regexstr, len(cells), string.ascii_uppercase)
        regexes.append((regexstr, regex, cells))
        print("  ...done")
    for i, regexstr in enumerate(definitions[26:]):
        print("{0:25}".format(regexstr), end="")
        cells = list(grid.traverse_lr2ul(i))
        regex = NFSM(regexstr, len(cells), string.ascii_uppercase)
        regexes.append((regexstr, regex, cells))
        print("  ...done")

    finished = False
    iteration = 0
    while not finished:
        # Step 1: go and apply board constraints to the regexes
        for _, r, cells in regexes:
            for i, cell in enumerate(cells):
                r.constrain_slot(i, cell)

        # Step 2: go and apply regex constraints to the board
        # finished will be set back to false if at least one cell changed
        finished = True
        for regexstr, r, cells in regexes:
            for i, cell in enumerate(cells):
                oldcell = cell.copy()
                cell &= r.peek_slot(i)
                if oldcell != cell:
                    finished = False

        # Step 3: print progress
        iteration += 1
        print("\nIteration {0}".format(iteration))
        for regexstr, _, cells in regexes:
            print("{0:25} {1}".format(regexstr, "".join(("".join(c) if len(c)==1 else "_") for c in cells)))


if __name__ == "__main__":
    main()
