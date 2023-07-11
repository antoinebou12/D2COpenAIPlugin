"""
PlantUML client library.

This library allows you to connect to a PlantUML server and render

PlantUML markup into PNG images.
"""

from os import makedirs, path
from io import open
from typing import List, Optional
from zlib import compress
import httpx

"""
Exceptions for PlantUML.
"""


class PlantUMLError(Exception):
    """
    Error in processing.
    """
    pass


class PlantUMLConnectionError(PlantUMLError):
    """
    Error connecting or talking to PlantUML Server.
    """
    pass


class PlantUMLHTTPError(Exception):
    """
    Request to PlantUML server returned HTTP Error.
    """
    def __init__(self, response, content):
        self.response = response
        self.content = content
        self.url = getattr(response, "request", None)
        self.url = self.url.url if self.url else "unknown URL"
        self.message = f"HTTP Error : {self.url} {response}"
        super(PlantUMLHTTPError, self).__init__(self.message)


# Example usage
diagram = """
@startuml
title Example Diagram
actor User
User -> "Website" : Requests Page
"Website" -> "Database" : Retrieves Data
"Database" --> "Website" : Returns Data
"Website" -> User : Sends Page
@enduml
"""

class PlantUML:
    """Connection to a PlantUML server with optional authentication.

    All parameters are optional.

    :param str url: URL to the PlantUML server image CGI. defaults to
                    http://www.plantuml.com/plantuml/img/
    :param dict basic_auth: This is if the plantuml server requires basic HTTP
                    authentication. Dictionary containing two keys, 'username'
                    and 'password', set to appropriate values for basic HTTP
                    authentication.
    :param dict form_auth: This is for plantuml server requires a cookie based
                    webform login authentication. Dictionary containing two
                    primary keys, 'url' and 'body'. The 'url' should point to
                    the login URL for the server, and the 'body' should be a
                    dictionary set to the form elements required for login.
                    The key 'method' will default to 'POST'. The key 'headers'
                    defaults to
                    {'Content-type':'application/x-www-form-urlencoded'}.
                    Example: form_auth={'url': 'http://example.com/login/',
                    'body': { 'username': 'me', 'password': 'secret'}
    :param dict http_opts: Extra options to be passed off to the
                    httplib2.Http() constructor.
    :param dict request_opts: Extra options to be passed off to the
                    httplib2.Http().request() call.

    """
    def __init__(self, url: str, basic_auth: dict = None, form_auth: dict = None, http_opts: dict = None, request_opts: dict = None) -> None:

        if basic_auth is None:
            basic_auth = {}
        if form_auth is None:
            form_auth = {}
        if http_opts is None:
            http_opts = {}
        if request_opts is None:
            request_opts = {}

        self.url = url
        self.request_opts = request_opts

        if auth_type := 'basic_auth' if basic_auth else ('form_auth' if form_auth else None):
            self.auth_type = auth_type

        self.auth = basic_auth or form_auth or None
        self.client = httpx.Client(**http_opts, proxies=http_opts.get('proxies'))

        if auth_type == 'basic_auth':
            self.client.auth = (username := self.auth['username'], self.auth['password'])
        elif auth_type == 'form_auth':
            if 'url' not in self.auth:
                raise PlantUMLError("The form_auth option 'url' must be provided and point to the login url.")
            if 'body' not in self.auth:
                raise PlantUMLError("The form_auth option 'body' must be provided and include a dictionary with the form elements required to log in. Example: form_auth={'url': 'http://example.com/login/', 'body': { 'username': 'me', 'password': 'secret'}}")
            login_url, body, method, headers = self.auth['url'], self.auth['body'], self.auth.get('method', 'POST'), self.auth.get('headers', {'Content-type': 'application/x-www-form-urlencoded'})
            try:
                response = self.client.request(method, login_url, headers=headers, data=body)
            except httpx.HTTPError as e:
                raise PlantUMLConnectionError(e) from e
            if response.status_code != 200:
                raise PlantUMLHTTPError(response, "Login failed. Check your form_auth settings.")
            self.request_opts['Cookie'] = response.cookies.get_dict()

    def get_url(self, plantuml_text):
        """Return the server URL for the image.
        You can use this URL in an IMG HTML tag.

        :param str plantuml_text: The plantuml markup to render
        :returns: the plantuml server image URL
        """
        return f'{self.url}/{self.deflate_and_encode(plantuml_text)}'

    def process(self, plantuml_text: str):
        """Processes the plantuml text into the raw PNG image data.
        :param str plantuml_text: The plantuml markup to render
        :returns: the raw image data
        """
        url = self.get_url(plantuml_text)
        try:
            response = self.client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise PlantUMLHTTPError(e, "") from e
        return response.content, url

    def process_file(self, filename, outfile=None, errorfile=None, directory=''):
        """Take a filename of a file containing plantuml text and processes
        it into a .png image.
        ...
        """
        data = open(filename).read()
        try:
            content, url = self.process(data)
            if not content:  # Add this check
                raise PlantUMLHTTPError("Server returned an error", "")
        except PlantUMLHTTPError as e:
            with open(path.join(directory, errorfile), 'w') as err:
                err.write(e.content)
            return False
        with open(path.join(directory, outfile), 'wb') as out:
            out.write(content)
        return True


    def deflate_and_encode(self, plantuml_text):
        """zlib compress the plantuml text and encode it for the plantuml server.

        :param str plantuml_text: The plantuml markup to render
        :returns: The encoded plantuml markup
        """
        zlibbed_str = compress(plantuml_text.encode('utf-8'))
        compressed_string = zlibbed_str[2:-4]
        return self.encode(compressed_string)


    def encode(self, data: bytes):
        """encode the plantuml data which may be compresses in the proper
        encoding for the plantuml server

        :param bytes data: The data to encode
        :returns: The encoded data
        """
        res = ""
        for i in range(0, len(data), 3):
            if i + 2 == len(data):
                res += self._encode3bytes(data[i], data[i + 1], 0)
            elif i + 1 == len(data):
                res += self._encode3bytes(data[i], 0, 0)
            else:
                res += self._encode3bytes(data[i], data[i + 1], data[i + 2])
        return res


    def _encode3bytes(self, b1: int, b2: int, b3: int):
        """
        Encode 3 bytes into 4 characters

        :param b1: The first byte
        :param b2: The second byte
        :param b3: The third byte
        :return: The encoded characters
        """
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        res = ""
        res += self._encode6bit(c1 & 0x3F)
        res += self._encode6bit(c2 & 0x3F)
        res += self._encode6bit(c3 & 0x3F)
        res += self._encode6bit(c4 & 0x3F)
        return res


    def _encode6bit(self, b):
        """
        Encode 6 bits into a single character

        :param b: The byte to encode
        :return: The encoded character
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

    def generate_image_from_string(
            self, plantuml_text: str, outfile: str) -> List[bytes, str, str]:
        """Generate an image from a string containing plantuml markup.

        :param str plantuml_text: The plantuml markup to render
        :param str outfile: Filename to write the output image to.
        :returns: ``True`` if the image write succedded, ``False`` if there was
        :raises: PlantUMLHTTPError if there was an error
        """

        try:
            content, url = self.process(plantuml_text)
        except PlantUMLHTTPError as e:
            raise PlantUMLHTTPError(e, "") from e
        with open(outfile, 'wb') as out:
            out.write(content)
        return content, url, outfile