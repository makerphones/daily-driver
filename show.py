# SPDX-FileCopyrightText: 2026 Jamey Warren
# SPDX-License-Identifier: MIT

"""
Show the cup + baffle assembly in OCP CAD Viewer.

Needs the `ocp_vscode` package and the OCP CAD Viewer open in VS Code:
    pip install ocp_vscode
Then run:
    python show.py
"""

import sys

from assembly import make_assembly


def main() -> int:
    try:
        from ocp_vscode import show
    except ImportError:
        print(
            "ocp_vscode not installed. Install it and open the OCP CAD Viewer "
            "panel in VS Code:\n  pip install ocp_vscode\n"
            "Or open output/assembly.step (from build.py) in any STEP viewer.",
            file=sys.stderr,
        )
        return 1
    show(make_assembly(), name="daily_driver_cup_baffle")
    print("Sent assembly to OCP CAD Viewer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
