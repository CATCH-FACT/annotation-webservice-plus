#! /usr/bin/python

from annotator import AbstractAnnotator
from frogclient import FrogClient

"""
Carries out named entity recognition using FROG
"""


class NerAnnotator(AbstractAnnotator):
    """
    Creates a new named entity recognizer based on frogclient
    frog_url indicates the frog server to use, e.g. "localhost:12345" (host:port)
    """
    def __init__(self, frog_url):
        super(NerAnnotator, self).__init__()
        try:
            (host, port) = frog_url.split(":")
            self.host = host
            self.port = port
        except ValueError:
            raise Exception("{} is not a valid frog host and port".format(frog_url))

    def process(self, doc):
        text = doc.get("text", '')
        try:
            frogclient = FrogClient(host=self.host, port=self.port, returnall=True)
            named_entities = frogclient.named_entities(text)
            return {
                "status": "OK",
                "message": "Automatically detected named entities",
                "annotation": {
                    "entities": list(set(named_entities)),
                }
            }
        except Exception as e:
            print(e)
            return {
                "status": "ERROR",
                "message": "Could not retrieve named entities (is frog running?)"
            }
