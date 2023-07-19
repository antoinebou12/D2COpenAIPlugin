import base64
import zlib
from enum import Enum

class Layout(Enum):
    DAGRE = 'dagre'
    ELK = 'elk'
    TALA = 'tala'

class Theme(Enum):
    DEFAULT = '0'
    DARK = '103'

def decode(encoded: str):
    compressed = base64.urlsafe_b64decode(encoded)
    decompressed = zlib.decompress(compressed)
    return decompressed.decode()

def encode(raw: str):
    utf16_encoded = raw.encode('utf-16')
    compressed = zlib.compress(utf16_encoded)
    return base64.urlsafe_b64encode(compressed).decode()

def generate_d2graphviz_url(edge_def, layout=Layout.DAGRE, theme=Theme.DEFAULT):
    # Compress and Base64 encode the edge definition
    encoded_edge_def = encode(edge_def)

    return f"https://play.d2lang.com/?script={encoded_edge_def}&layout={layout.value}&theme={theme.value}"


# Example usage
if __name__ == "__main__":
    edge_def = """
    aws: {
      db: "" {
        icon: https://icons.terrastruct.com/azure/Databases%20Service%20Color/Azure%20Database%20for%20PostgreSQL%20servers.svg
        shape: image
      }

      cache: "" {
        icon: https://icons.terrastruct.com/azure/_Companies/Azure%20Cache%20Redis%20Product%20icon.svg
        shape: image
      }

      ec2: "" {
        icon: https://icons.terrastruct.com/aws/_Group%20Icons/EC2-instance-container_light-bg.svg
        shape: image
      }

      ec2 <-> db: get persisted data
      ec2 <-> cache: get temporal data
    }

    gcloud: {
      db: "" {
        icon: https://icons.terrastruct.com/azure/Databases%20Service%20Color/Azure%20Database%20for%20PostgreSQL%20servers.svg
        shape: image
      }
    }

    aws.db -> gcloud.db: backup

    dev: "" {
      icon: https://icons.terrastruct.com/essentials/005-programmer.svg
      shape: image
    }

    github: "" {
      icon: https://icons.terrastruct.com/dev/github.svg
      shape: image
    }

    dev -> aws.ec2: ssh
    dev -> github: version control
    """

    url = generate_d2graphviz_url(edge_def, layout=Layout.ELK, theme=Theme.DARK)
    print("Generated URL:", url)

    encoded = "zJJPi9w8DMbv_hRiwcfExvBewstCmZZS6GHb_QCDYqsZ0yQOkpOBlvnuRZmdpT30z_bUm20eSz89evAsHXw1AKnv4O5uPwLoSB2cal2kc05v0lZiRqm8xtrGMjn8sjK511ixRyGxwT8SbzmSDf6gjrpXqrDB3zQ2-E-FbfAPRerA9PjhvQ1eiDdiaWUb9t67Hx3kCQcyABdjACLGE_0V3_FQpgXnTPKMc9BiNviPlLJiP3BJa6w2eC30Sw6K4aUUZ3HHt1zWxQb_TiXuzSE0eZaKc6QmaozyTHwcNVlNP_wOAP5v7vdtDVRhIZYslRIkrPid4Mkx1VSalsI4XiUXY4Y4ljX962u_GINnaVMPzT1ckVul7TF-XhdjEm3P6H8CTiI014yjOO__axYuA-M0ET8h_ACgLuV6WvsXtUi0ueu3n9RMtOk0OtceJZHT7e3WTk3JZQYNBpfRfAsAAP__"
    decoded = decode(encoded)
    print(decoded)
