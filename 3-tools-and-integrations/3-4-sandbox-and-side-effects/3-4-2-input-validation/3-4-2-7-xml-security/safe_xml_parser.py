from dataclasses import dataclass
from typing import Optional

from defusedxml.ElementTree import fromstring as safe_fromstring
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class XMLParseResult:
    success: bool
    root: Optional[ET.Element]
    error: Optional[str]


def parse_xml_safely(xml_data: str) -> XMLParseResult:
    """
    Parse XML securely using defusedxml.
    Protects against XXE attacks.
    """

    try:
        root = safe_fromstring(xml_data)
        return XMLParseResult(True, root, None)
    except ET.ParseError as exc:
        return XMLParseResult(False, None, f"XML parse error: {exc}")
    except Exception as exc:
        return XMLParseResult(False, None, f"Security violation: {exc}")


def main() -> None:
    safe_xml = """<?xml version="1.0"?>
    <user><name>Alice</name></user>
    """

    dangerous_xml = """<?xml version="1.0"?>
    <!DOCTYPE foo [
      <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <user><name>&xxe;</name></user>
    """

    print("SAFE:", parse_xml_safely(safe_xml))
    print("\nDANGEROUS:", parse_xml_safely(dangerous_xml))


if __name__ == "__main__":
    main()
