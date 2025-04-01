"""
Kroki client library for Python.

This library allows generating diagrams using the Kroki service.
Kroki is a unified API for generating diagrams from textual descriptions.
"""

import base64
import zlib
import httpx
import logging
import json
from typing import Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# Dictionary of supported diagram types and their output formats
LANGUAGE_OUTPUT_SUPPORT = {
    "actdiag": ["png", "svg", "pdf"],
    "blockdiag": ["png", "svg", "pdf"],
    "bpmn": ["svg"],
    "bytefield": ["svg"],
    "c4plantuml": ["png", "svg", "pdf", "txt", "base64"],
    "d2": ["png", "svg"],
    "dbml": ["svg"],
    "ditaa": ["png", "svg"],
    "erd": ["png", "svg", "pdf"],
    "excalidraw": ["svg"],
    "graphviz": ["png", "svg", "pdf", "jpeg"],
    "mermaid": ["svg", "png"],
    "nomnoml": ["svg"],
    "nwdiag": ["png", "svg", "pdf"],
    "packetdiag": ["png", "svg", "pdf"],
    "pikchr": ["svg"],
    "plantuml": ["png", "svg", "pdf", "txt", "base64"],
    "rackdiag": ["png", "svg", "pdf"],
    "seqdiag": ["png", "svg", "pdf"],
    "structurizr": ["png", "svg", "pdf", "txt", "base64"],
    "svgbob": ["svg"],
    "symbolator": ["svg"],
    "tikz": ["png", "svg", "jpeg", "pdf"],
    "umlet": ["png", "svg", "jpeg"],
    "vega": ["svg", "png"],
    "vegalite": ["svg", "png"],
    "wavedrom": ["svg"],
    "wireviz": ["png", "svg"],
}


class KrokiError(Exception):
    """Base exception for Kroki errors."""
    pass


class KrokiConnectionError(KrokiError):
    """Error connecting or talking to Kroki Service."""
    pass


class KrokiHTTPError(KrokiError):
    """Request to Kroki server returned HTTP Error."""
    def __init__(self, response, content):
        self.response = response
        self.content = content
        self.url = response.url
        self.message = f"HTTP Error: {self.url} {response.status_code}"
        super(KrokiHTTPError, self).__init__(self.message)


class Kroki:
    """Client for the Kroki diagram generation service.
    
    Kroki provides a unified API for generating diagrams from textual descriptions.
    This client supports multiple diagram types including PlantUML, Mermaid, D2, and more.
    
    Attributes:
        base_url: The base URL of the Kroki service.
        client: The HTTP client for making requests.
    """
    
    DIAGRAM_TYPES = LANGUAGE_OUTPUT_SUPPORT
    
    DIAGRAM_PLAYGROUNDS = {
        "mermaid": "https://mermaid.live/edit#",
        "plantuml": "https://www.plantuml.com/plantuml/uml/",
        "d2": "https://play.d2lang.com/?script=",
        "graphviz": "https://dreampuf.github.io/GraphvizOnline/#",
    }
    
    def __init__(self, base_url: str = "https://kroki.io", **http_opts):
        """
        Initialize the Kroki client.
        
        Args:
            base_url: The base URL of the Kroki service.
            **http_opts: Additional options to pass to the httpx client.
        """
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(**http_opts)
    
    def get_url(self, diagram_type: str, diagram_text: str, output_format: str = "svg") -> str:
        """
        Generate the URL for a diagram.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            diagram_text: The textual description of the diagram
            output_format: The desired output format (svg, png, etc.)
            
        Returns:
            The URL where the diagram can be accessed
            
        Raises:
            ValueError: If the diagram type or output format is not supported
        """
        if diagram_type not in self.DIAGRAM_TYPES:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
        
        supported_formats = self.DIAGRAM_TYPES[diagram_type]
        if output_format not in supported_formats:
            raise ValueError(
                f"Unsupported output format '{output_format}' for {diagram_type}. "
                f"Supported formats: {', '.join(supported_formats)}"
            )
            
        encoded_diagram = self.deflate_and_encode(diagram_text)
        return f"{self.base_url}/{diagram_type}/{output_format}/{encoded_diagram}"
    
    def get_playground_url(self, diagram_type: str, diagram_text: str) -> Optional[str]:
        """
        Generate a URL to an online playground for editing the diagram.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            diagram_text: The textual description of the diagram
            
        Returns:
            A URL to an online playground or None if not available
        """
        if diagram_type not in self.DIAGRAM_PLAYGROUNDS:
            return None
            
        base_playground = self.DIAGRAM_PLAYGROUNDS[diagram_type]
        
        # Different encodings for different playgrounds
        if diagram_type == "plantuml":
            encoded = self.encode_plantuml(diagram_text)
            return f"{base_playground}{encoded}"
        elif diagram_type == "mermaid":
            # Mermaid uses a special pako encoding
            state = {
                "code": diagram_text.strip(),
                "mermaid": {"theme": "default"},
                "updateEditor": True,
                "autoSync": True,
                "updateDiagram": True
            }
            serialized_state = self.serialize_state(state)
            return f"{base_playground}{serialized_state}"
        else:
            # Default: Just URI-encode the diagram text
            encoded = base64.urlsafe_b64encode(diagram_text.encode('utf-8')).decode('utf-8')
            return f"{base_playground}{encoded}"
    
    def render_diagram(self, diagram_type: str, diagram_text: str, output_format: str = "svg") -> bytes:
        """
        Render a diagram and return the image data.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            diagram_text: The textual description of the diagram
            output_format: The desired output format (svg, png, etc.)
            
        Returns:
            The binary content of the rendered diagram
            
        Raises:
            KrokiHTTPError: If there was an HTTP error
            KrokiConnectionError: If there was a connection error
        """
        url = self.get_url(diagram_type, diagram_text, output_format)
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise KrokiHTTPError(e.response, e.response.content)
        except httpx.RequestError as e:
            raise KrokiConnectionError(f"Error connecting to Kroki: {str(e)}")
            
        return response.content
    
    def generate_diagram(self, diagram_type: str, diagram_text: str, output_format: str = "svg") -> Dict:
        """
        Generate a diagram and return URLs and data.
        
        Args:
            diagram_type: The type of diagram (plantuml, mermaid, etc.)
            diagram_text: The textual description of the diagram
            output_format: The desired output format (svg, png, etc.)
            
        Returns:
            A dictionary containing:
            - url: The URL where the diagram can be accessed
            - content: The binary content of the rendered diagram
            - playground: URL to an online playground (if available)
            
        Raises:
            KrokiHTTPError: If there was an HTTP error
            KrokiConnectionError: If there was a connection error
        """
        url = self.get_url(diagram_type, diagram_text, output_format)
        playground = self.get_playground_url(diagram_type, diagram_text)
        
        try:
            response = self.client.get(url)
            response.raise_for_status()
            content = response.content
        except httpx.HTTPStatusError as e:
            raise KrokiHTTPError(e.response, e.response.content)
        except httpx.RequestError as e:
            raise KrokiConnectionError(f"Error connecting to Kroki: {str(e)}")
            
        return {
            "url": url,
            "content": content,
            "playground": playground
        }
    
    def deflate_and_encode(self, text: str) -> str:
        """
        Compress the text with zlib and encode it for the Kroki server.
        
        Args:
            text: The text to compress and encode
            
        Returns:
            The compressed and encoded text
        """
        if not text:
            return ""
        
        try:
            compress_obj = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15,
                                           memLevel=8, strategy=zlib.Z_DEFAULT_STRATEGY)
            compressed_data = compress_obj.compress(text.encode('utf-8'))
            compressed_data += compress_obj.flush()
            
            encoded = base64.urlsafe_b64encode(compressed_data).decode('ascii')
            return encoded.replace('+', '-').replace('/', '_')
        except Exception as e:
            logger.error(f"Error compressing and encoding text: {str(e)}")
            raise
    
    def encode_plantuml(self, text: str) -> str:
        """
        Encode text for PlantUML server.
        
        Args:
            text: The PlantUML diagram text
            
        Returns:
            The encoded text suitable for PlantUML server URLs
        """
        zlibbed_str = zlib.compress(text.encode('utf-8'))
        compressed_str = zlibbed_str[2:-4]  # Remove zlib header and checksum
        
        # PlantUML uses a custom encoding
        res = ""
        for i in range(0, len(compressed_str), 3):
            if i + 2 == len(compressed_str):
                res += self._encode_3bytes(
                    compressed_str[i], 
                    compressed_str[i + 1], 
                    0
                )
            elif i + 1 == len(compressed_str):
                res += self._encode_3bytes(
                    compressed_str[i], 
                    0, 
                    0
                )
            else:
                res += self._encode_3bytes(
                    compressed_str[i], 
                    compressed_str[i + 1], 
                    compressed_str[i + 2]
                )
        return res
    
    def _encode_3bytes(self, b1: int, b2: int, b3: int) -> str:
        """
        Encode 3 bytes using PlantUML's encoding.
        
        Args:
            b1: First byte
            b2: Second byte
            b3: Third byte
            
        Returns:
            Four encoded characters
        """
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        
        res = ""
        res += self._encode_6bit(c1 & 0x3F)
        res += self._encode_6bit(c2 & 0x3F)
        res += self._encode_6bit(c3 & 0x3F)
        res += self._encode_6bit(c4 & 0x3F)
        return res
    
    def _encode_6bit(self, b: int) -> str:
        """
        Encode 6 bits using PlantUML's encoding.
        
        Args:
            b: The 6 bits to encode
            
        Returns:
            A single encoded character
        """
        if b < 10:
            return chr(48 + b)
        b -= 10
        if b < 26:
            return chr(65 + b)
        b -= 26
        if b < 26:
            return chr(97 + b)
        b -= 26
        if b == 0:
            return '-'
        return '_' if b == 1 else '?'
    
    def serialize_state(self, state: Dict) -> str:
        """
        Serialize state for Mermaid Live Editor.
        
        Args:
            state: Dictionary containing Mermaid state
            
        Returns:
            Serialized state string
        """
        json_str = json.dumps(state)
        
        # Compress with zlib
        compressed = zlib.compress(json_str.encode('utf-8'), level=9)
        # Base64 encode
        b64 = base64.urlsafe_b64encode(compressed).decode('utf-8')
        # Add pako prefix
        return f"pako:{b64}"


# For backward compatibility - wrap the Kroki class methods
def generate_kroki_url(diagram_type: str, diagram_source: str, output_format: str = "svg") -> str:
    """
    Generate a URL for the Kroki diagram
    
    Args:
        diagram_type: Type of diagram (e.g., "plantuml", "mermaid")
        diagram_source: Source code for the diagram
        output_format: Output format (e.g., "svg", "png")
        
    Returns:
        URL for the diagram
    """
    kroki = Kroki()
    return kroki.get_url(diagram_type, diagram_source, output_format)


async def generate_diagram(diagram_type: str, diagram_source: str, output_format: str = "svg") -> Tuple[str, str, str]:
    """
    Generate a diagram using Kroki API
    
    Args:
        diagram_type: Type of diagram (e.g., "plantuml", "mermaid")
        diagram_source: Source code for the diagram
        output_format: Output format (e.g., "svg", "png")
        
    Returns:
        Tuple of (url, content, playground_url)
    """
    try:
        kroki = Kroki()
        url = kroki.get_url(diagram_type, diagram_source, output_format)
        playground = kroki.get_playground_url(diagram_type, diagram_source)
        
        # For backwards compatibility, return content as the source code
        content = diagram_source
        
        return url, content, playground or ""
    except Exception as e:
        logger.error(f"Error generating {diagram_type} diagram: {str(e)}")
        raise
