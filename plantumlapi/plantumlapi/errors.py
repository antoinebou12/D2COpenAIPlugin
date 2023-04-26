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
