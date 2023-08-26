#!/usr/bin/env python3

"""
svg2gpl.py: A script to extract colors from an SVG file and save them as a GIMP palette.

This script takes an SVG file as input and extracts color information from its 'fill' and 'stroke' attributes.
It then converts the extracted colors to a GIMP palette format and saves it to an output file.

Usage: python svg_to_gpl.py input.svg output.gpl
"""

import sys

from palette import GPL_palette

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python svg_to_gpl.py input.svg output.gpl")
        sys.exit(1)

    input_svg_filename = sys.argv[1]
    output_gpl_filename = sys.argv[2]

    gpl_palette = GPL_palette.extract_from_svg(input_svg_filename)
    gpl_palette.save(output_gpl_filename)

    print(
        f"Colors extracted from {input_svg_filename} and \saved as GIMP palette: {output_gpl_filename}"
    )
