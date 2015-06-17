#! /usr/bin/python

"""
Counts words in a text.
"""
from annotator import AbstractAnnotator
import re

class WordcountClassAnnotator(AbstractAnnotator):
    def __init__(self):
        super(WordcountClassAnnotator, self).__init__()

    def determine_text_length(self, t):
        try:
            return len(re.findall("\w+", t))
        except:
            try:
                return len(re.findall("\w+", " ".join(t)))
            except:
                return -1

    def classify_length(self, length):
        if length < 20:
            return '<25'
        if length < 100:
            return '25-100'
        elif length < 250:
            return '100-250'
        elif length < 500:
            return '250-500'
        elif length < 1000:
            return '500-1000'
        else:
            return '>1000'
                
    def process(self, doc):
        text = doc.get("text", '').strip()

        if text == '':
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            tl = self.classify_length(self.determine_text_length(text));

            return {
                "status": "OK",
                "message": "Automatically detected word count class",
                "annotation": {
                    "value": tl,
                }
            }

