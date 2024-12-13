"""
This script processes an XML file to generate mock data and optionally
adjust specified nodes.

Features:
- Generates random mock data based on inferred data types (int, float, date,
  string).
- Adjusts a specified XML node to have an exact count,
  preserving its structure.
- Modifies the input file in-place if the --replace flag is used or saves to a
  specified output file.

Usage:
python xml_file_mocker.py input --output OUTPUT_FILE --node NODE_NAME --count
DUPLICATION_COUN --replace
"""

import xml.etree.ElementTree as ET
import random
import argparse

try:
    from faker import Faker
except ImportError:
    import subprocess
    import sys
    try:
        subprocess.check_call([
            sys.executable, "-m", "ensurepip", "--upgrade"
        ])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "faker"
        ])
        from importlib import import_module
        Faker = import_module("faker").Faker
    except Exception as e:
        print(
            "Failed to install required module 'faker'. "
            "Please install it manually."
        )
        print(f"Error: {e}")
        sys.exit(1)

fake = Faker()


def generate_mock_data(data_type):
    """
    Generates random mock data based on the given data type.

    Args:
        data_type (str): The type of data to generate (e.g., 'int', 'float',
                        'date', 'string').

    Returns:
        str: A random value of the specified data type.
    """
    if data_type == 'int':
        return str(random.randint(0, 100))
    elif data_type == 'float':
        return str(round(random.uniform(0, 100), 2))
    elif data_type == 'date':
        return fake.date()
    else:
        return fake.word()


def infer_data_type(value):
    """
    Infers the data type of a given value.

    Args:
        value (str): The value to infer the data type from.

    Returns:
        str: The inferred data type ('int', 'float', 'date', or 'string').
    """
    if value.isdigit():
        return 'int'
    try:
        float(value)
        return 'float'
    except ValueError:
        pass
    try:
        if '-' in value or '/' in value:
            fake.date_pattern_validator(value)
            return 'date'
    except Exception:
        pass
    return 'string'


def adjust_node_count(parent, target_node, desired_count):
    """
    Adjusts the number of target nodes to match the desired count,
    preserving the full structure of the nodes when duplicating.

    Args:
        parent (xml.etree.ElementTree.Element): The parent node containing the
                                                target nodes.
        target_node (str): The name of the target node to adjust.
        desired_count (int): The desired number of target nodes.
    """
    current_nodes = [child for child in parent if child.tag == target_node]
    current_count = len(current_nodes)

    # Remove excess nodes if necessary
    if current_count > desired_count:
        for node in current_nodes[desired_count:]:
            parent.remove(node)

    # Add new nodes if necessary
    elif current_count < desired_count:
        template_node = current_nodes[0] if current_nodes else None
        for _ in range(desired_count - current_count):
            if template_node is not None:
                # Deep copy the node structure
                new_node = ET.Element(template_node.tag, template_node.attrib)
                for child in template_node:
                    new_child = ET.Element(child.tag, child.attrib)
                    new_child.text = child.text
                    new_child.extend(list(child))
                    new_node.append(new_child)
                parent.append(new_node)
            else:
                # If no existing node, create a blank node with mock data
                new_node = ET.Element(target_node)
                new_node.text = generate_mock_data('string')
                parent.append(new_node)


def process_node(node, target_node, desired_count):
    """
    Recursively processes an XML node, adjusting the number of target nodes
    to match the desired count and replacing data after adjustments.

    Args:
        node (xml.etree.ElementTree.Element): The current XML node.
        target_node (str): The name of the node to adjust.
        desired_count (int): The desired number of target nodes.
    """
    # Adjust child nodes if this node is the parent of the target node
    if target_node in [child.tag for child in node]:
        adjust_node_count(node, target_node, desired_count)

    # Replace data for this node and its children
    if node.text and node.text.strip():
        data_type = infer_data_type(node.text.strip())
        node.text = generate_mock_data(data_type)

    for child in list(node):
        process_node(child, target_node, desired_count)

gg
def mock_xml(input_file, output_file, target_node, desired_count):
    """
    Processes the XML file to generate mock data and adjust the number of
    target nodes to match the desired count.

    Args:
        input_file (str): Path to the input XML file.
        output_file (str): Path to save the output XML file.
        target_node (str): The name of the node to adjust.
        desired_count (int): The desired number of target nodes.
    """
    tree = ET.parse(input_file)
    root = tree.getroot()

    process_node(root, target_node, desired_count)

    tree.write(output_file, encoding="utf-8", xml_declaration=True)


def main():
    """
    Parses command-line arguments and executes the XML processing.
    """
    parser = argparse.ArgumentParser(
        description="Mock XML Data"
    )
    parser.add_argument(
        "input",
        help="Path to the input XML file"
    )
    parser.add_argument(
        "--output",
        help=(
            "Path to save the output XML file (optional if --replace is used)"
        ),
        default=None
    )
    parser.add_argument(
        "--node",
        type=str,
        default=None,
        help="Name of the XML node to adjust"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="Desired number of the specified nodes"
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help=(
            "Modify the input file in-place instead of creating an output file"
        )
    )

    args = parser.parse_args()

    output_file = args.input if args.replace else args.output

    if not output_file:
        raise ValueError(
            "Output file must be specified unless --replace is used."
        )

    mock_xml(
        args.input,
        output_file,
        args.node,
        args.count
    )


if __name__ == "__main__":
    main()
