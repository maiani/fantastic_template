import json
import re
import xml.etree.ElementTree as ET
from collections import OrderedDict
from typing import Dict, Tuple, Type
import os

import numpy as np
from drawsvg import Drawing, Rectangle


def load_color_data(json_path: str) -> Dict[str, Tuple[int, int, int]]:
    """
    Load color data from a JSON file.

    Args:
        json_path (str): Path to the JSON color data file.

    Returns:
        dict: A dictionary containing color names as keys and RGB tuples as values.
    """
    with open(json_path, "r") as json_file:
        color_data = json.load(json_file)
    return color_data


def find_closest_color(
    target_rgb: Tuple[int, int, int], color_data: Dict[str, Tuple[int, int, int]]
) -> str:
    """
    Find the closest color name in the color data based on RGB distance from a hex value.

    Args:
        target_rgb (str): RGB list as values.
        color_data (dict): Dictionary containing color names as keys and RGB tuples as values.

    Returns:
        str: The closest color name.
    """

    color_names = list(color_data.keys())
    color_rgbs = np.array(list(color_data.values()))

    rgb_distances = np.sqrt(np.sum((np.array(color_rgbs) - target_rgb) ** 2, axis=1))
    closest_color_index = np.argmin(rgb_distances)

    return color_names[closest_color_index]


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """
    Convert a hex color value to an RGB tuple.

    Args:
        value (str): Hexadecimal color value (e.g., '#FF0000').

    Returns:
        tuple: RGB tuple (red, green, blue) corresponding to the hex color value.
    """
    value = value.lstrip("#")
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


class GPL_palette:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.colors = OrderedDict()
        self.comment = None

    def add_color(self, color_name, rgb_list):
        self.colors[color_name] = rgb_list

    def save(self, output_gpl_file: str):
        """
        Save the extracted colors as a GIMP palette file.

        Args:
            output_gpl_file (str): Path to the output GIMP palette file.
        """
        with open(output_gpl_file, "w") as output_file:
            output_file.write("GIMP Palette\n")
            output_file.write(f"Name: {self.name}\n")
            if self.comment:
                output_file.write(f"# {self.comment}\n")
            output_file.write(f"Columns: {self.columns}\n")

            for color_name, rgb_list in self.colors.items():
                # Convert RGB list to formatted string
                rgb_color = " ".join(str(value) for value in rgb_list)
                output_file.write(f"{rgb_color} {color_name}\n")

    def load(gpl_filename: str) -> Type["GPL_palette"]:
        """
        Load colors from a GIMP palette (GPL) file and populate the GPL_palette instance.

        Args:
            gpl_filename (str): Path to the GIMP palette (GPL) file.
        """
        if not gpl_filename.endswith(".gpl"):
            raise ValueError("Invalid file format. Expected a .gpl file.")

        color_pattern = re.compile(r"(\d+)\s+(\d+)\s+(\d+)\s+(.+)")

        palette = GPL_palette(
            "Placeholder Name", columns=0
        )  # Create a placeholder palette

        with open(gpl_filename, "r") as gpl_file:
            lines = gpl_file.readlines()

            for line in lines:
                line = line.strip()
                if line.startswith("Name:"):
                    palette.name = line.split(":", 1)[1].strip()
                elif line.startswith("Columns:"):
                    palette.columns = int(line.split(":", 1)[1].strip())
                elif line.startswith("#"):
                    palette.comment = line[1:]
                elif line and line[0].isdigit():
                    match = color_pattern.match(line)
                    if match:
                        r, g, b, color_name = match.groups()
                        palette.add_color(color_name, [int(r), int(g), int(b)])

        return palette

    def generate_latex(self) -> str:
        """
        Generate LaTeX code for color definitions.
        """
        latex_code = "% Define the colors you want\n"
        latex_code += "\\usepackage{xcolor}\n"

        for color_name, rgb_list in self.colors.items():
            r, g, b = rgb_list
            latex_color_name = color_name.replace(" ", "_")
            latex_color_definition = (
                "\\definecolor{"
                + latex_color_name
                + "}{RGB}{"
                + f"{r}, {g}, {b}"
                + "}\n"
            )
            latex_code += latex_color_definition

        return latex_code

    # SVG methods
    @staticmethod
    def extract_from_svg(svg_file: str, columns=3) -> Type["GPL_palette"]:
        """
        Extract unique color values from an SVG file's 'fill' and 'stroke' attributes.

        Args:
            svg_file (str): Path to the SVG file.

        Returns:
            GPL_palette: A GPL_palette instance containing extracted color information.
        """
        color_data = load_color_data("colors.json")

        base_filename = os.path.basename(svg_file)
        filename_without_extension = os.path.splitext(base_filename)[0]
        palette = GPL_palette(filename_without_extension, columns=columns)
        palette.comment = f"Extracted from {base_filename}"

        tree = ET.parse(svg_file)
        root = tree.getroot()

        color_pattern = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")

        for element in root.iter():
            for attr_name in ["fill", "stroke"]:
                if attr_name in element.attrib:
                    color_value = element.attrib[attr_name]
                    color_matches = color_pattern.findall(color_value)
                    for hex_color in color_matches:
                        rgb_color = hex_to_rgb(hex_color)
                        palette.add_color(
                            find_closest_color(rgb_color, color_data), rgb_color
                        )

        return palette

    def create_svg(self, output_svg_path: str, colors_per_row: int = 2):
        """
        Create an SVG file with a grid of squares for each color.

        Args:
            colors (OrderedDict): Ordered dictionary containing color names as keys and RGB color lists as values.
            output_svg_path (str): Path to the output SVG file.
            colors_per_row (int, optional): Number of colors per row in the grid. Default is 2.
        """
        num_colors = len(self.colors)
        rows = (
            num_colors + colors_per_row - 1
        ) // colors_per_row  # Calculate number of rows based on colors_per_row

        square_size = 10  # 10mm per side

        svg_width = colors_per_row * square_size
        svg_height = rows * square_size

        drawing = Drawing(svg_width, svg_height)

        color_list = list(
            self.colors.items()
        )  # Convert OrderedDict items to a list of (color_name, rgb_list) tuples

        for row in range(rows):
            for col in range(colors_per_row):
                color_index = row * colors_per_row + col
                if color_index >= num_colors:
                    break

                x = col * square_size
                y = row * square_size

                color_name, rgb_list = color_list[color_index]
                rgb_string = "rgb({}, {}, {})".format(*rgb_list)
                rect = Rectangle(x, y, square_size, square_size, fill=rgb_string)
                drawing.append(rect)

        drawing.save_svg(output_svg_path)
