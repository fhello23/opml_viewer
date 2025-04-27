# opml_parser.py
# (Keep the previous version - it already extracts the 'topic')
import xml.etree.ElementTree as ET
import re

def _clean_text(text):
    """Removes extra whitespace and newlines."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def _get_details_recursive(outline_element, depth=0):
    """Recursively extracts text from an outline and its children, indented."""
    details = []
    indent = "  " * depth
    element_text = _clean_text(outline_element.get('text'))
    if element_text:
         details.append(f"{indent}- {element_text}")

    for child in outline_element.findall('outline'):
        details.extend(_get_details_recursive(child, depth + 1))

    return details


def parse_opml(filepath='ttos.op'):
    """Parses the OPML file from a file path and extracts 'cards'."""
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()
        return _process_opml_root(root)
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []
    except ET.ParseError:
        print(f"Error: Could not parse XML in {filepath}")
        return []


def parse_opml_file(file_obj):
    """Parses the OPML from a file-like object and extracts 'cards'."""
    try:
        tree = ET.parse(file_obj)
        root = tree.getroot()
        return _process_opml_root(root)
    except ET.ParseError as e:
        print(f"Error: Could not parse XML from file object: {e}")
        return []


def _process_opml_root(root):
    """Process the parsed OPML root and extract cards."""
    cards = []
    body = root.find('body')
    if body is None:
        return []

    for topic_outline in body.findall('outline'):
        topic_text = _clean_text(topic_outline.get('text'))

        for term_outline in topic_outline.findall('outline'):
            term_text = _clean_text(term_outline.get('text'))

            if term_outline.find('outline') is not None:
                raw_details = []
                for detail_outline in term_outline.findall('outline'):
                   raw_details.extend(_get_details_recursive(detail_outline, depth=0))

                details_list = [d for d in raw_details if d and d != '-']

                if term_text and details_list:
                    cards.append({
                        'topic': topic_text,
                        'term': term_text,
                        'details': details_list
                    })

    return cards

# Example usage (optional, for testing)
if __name__ == '__main__':
    parsed_cards = parse_opml()
    if parsed_cards:
        print(f"Parsed {len(parsed_cards)} cards.")
