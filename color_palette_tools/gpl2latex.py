#!/usr/bin/env python3

"""
gpl2latex.py: A script to generate LaTeX color definitions from a GIMP palette (GPL) file.

This script reads colors from a GIMP palette (GPL) file and generates LaTeX color definitions.

Usage: python gpl2latex.py input.gpl
"""

import sys

from palette import GPL_palette

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python gpl2latex.py input.gpl")
        sys.exit(1)

    input_gpl_filename = sys.argv[1]

    gpl_palette = GPL_palette.load(input_gpl_filename)
    latex_code = gpl_palette.generate_latex()

    print(latex_code)
