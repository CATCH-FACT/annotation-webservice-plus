#! /usr/bin/python

"""
Counts words in a text.
"""
from annotator import AbstractAnnotator
import re

class WordcountAnnotator(AbstractAnnotator):
    def __init__(self):
        super(WordcountAnnotator, self).__init__()

    def determine_text_length(self, t):
        try:
            return len(re.findall("\w+", t))
        except:
            try:
                return len(re.findall("\w+", " ".join(t)))
            except:
                return -1

    def process(self, doc):
        text = doc.get("text", '').strip()

        if text == '':
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            tl = self.determine_text_length(text);

            return {
                "status": "OK",
                "message": "Automatically detected word count",
                "annotation": {
                    "value": tl,
                }
            }

