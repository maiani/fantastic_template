#!/usr/bin/env python3


"""
gpl2svg.py: A script to create an SVG file with a grid of squares for each color in a GIMP palette (GPL).

This script reads colors from a GIMP palette (GPL) file and generates an SVG file with a 2xN grid of squares,
each representing a color from the palette.

Usage: python gpl_to_svg.py input.gpl output.svg
"""

import sys

from palette import GPL_palette

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python gpl_to_svg.py input.gpl output.svg")
        sys.exit(1)

    input_gpl_filename = sys.argv[1]
    output_svg_filename = sys.argv[2]

    gpl_palette = GPL_palette.load(input_gpl_filename)
    gpl_palette.create_svg(output_svg_filename)

    print(
        f"SVG file with colors from {input_gpl_filename} created: {output_svg_filename}"
    )
