import zlib
import base64
import json
from urllib.parse import quote, unquote
import logging

logger = logging.getLogger(__name__)

def js_encode_uri_component(data):
    return quote(data, safe='~()*!.\'')


def js_decode_uri_component(data):
    return unquote(data)


def js_string_to_byte(data):
    return bytearray(data, 'UTF-8')


def js_bytes_to_string(data):
    return data.decode('UTF-8')


def js_btoa(data):
    return base64.b64encode(data)


def js_atob(data):
    return base64.b64decode(data)

class Serde:
    def serialize(self, state: str) -> str:
        raise NotImplementedError

    def deserialize(self, state: str) -> str:
        raise NotImplementedError

class Base64Serde(Serde):
    def serialize(self, state: str) -> str:
        result = base64.b64encode(state.encode()).decode()
        return result + '=' * ((4 - len(result) % 4) % 4)

    def deserialize(self, state: str) -> str:
        return base64.b64decode(state.encode()).decode()


class PakoSerde(Serde):
    def serialize(self, state: str) -> str:
        compressed = self.pako_deflate(state.encode('utf-8'))
        result = str(base64.urlsafe_b64encode(compressed), 'utf-8')
        return result + '=' * ((4 - len(result) % 4) % 4)

    def deserialize(self, state: str) -> str:
        data = base64.urlsafe_b64decode(state)
        decompressed = self.pako_inflate(data)
        return decompressed.decode('utf-8')

    def pako_deflate(self, data):
        compress  = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=15,
            memLevel=8, strategy=zlib.Z_DEFAULT_STRATEGY)
        compressed_data = compress.compress(data)
        compressed_data += compress.flush()
        return compressed_data

    def pako_inflate(self, data):
        decompress = zlib.decompressobj(15)
        decompressed_data = decompress.decompress(data)
        decompressed_data += decompress.flush()
        return decompressed_data

SERDES = {
    "base64": Base64Serde(),
    "pako": PakoSerde(),
}

def serialize_state(state: dict, serde: str = "pako") -> str:
    if serde not in SERDES:
        raise ValueError(f"Unknown serde type: {serde}")
    json_str = json.dumps(state)
    serialized = SERDES[serde].serialize(json_str)
    return f"{serde}:{serialized}"

def deserialize_state(state: str) -> dict:
    serde, serialized = state.split(":", 1) if ":" in state else ("base64", state)
    if serde not in SERDES:
        raise ValueError(f"Unknown serde type: {serde}")
    # Add the necessary padding
    required_padding = len(serialized) % 4
    if required_padding > 0:
        serialized += '='* (4 - required_padding)
    json_str = SERDES[serde].deserialize(serialized)
    return json.loads(json_str)

def generate_diagram_state(diagram_text, theme="dark", updateEditor=True, autoSync=True, updateDiagram=True):
    return {
        "code": diagram_text.strip(),
        "mermaid": {"theme": theme},
        "updateEditor": updateEditor,
        "autoSync": autoSync,
        "updateDiagram": updateDiagram
    }

def generate_mermaid_live_editor_url(diagram_state: dict, serde: str = "pako") -> tuple[str, str]:
    serialized_state = serialize_state(diagram_state, serde)
    return f"https://mermaid.ink/svg/{serialized_state}", diagram_state["code"], f"https://mermaid.live/edit#{serialized_state}"


if __name__ == "__main__":
    diagram_text = """graph TD
  A[Christmas] -->|Get money| B(Go shopping)
  B --> C{Let me think}
  C -->|One| D[Laptop]
  C -->|Two| E[iPhone]
  C -->|Three| F[fa:fa-car Car]"""
    trimmed_diagram_text = "\n".join(line.strip() for line in diagram_text.split("\n")).strip()

    diagram_state = generate_diagram_state(diagram_text)
    mermaid_live_editor_url = generate_mermaid_live_editor_url(diagram_state)
    print("Generated URL:", mermaid_live_editor_url)




