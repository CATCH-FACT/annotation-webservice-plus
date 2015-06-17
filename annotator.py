#! /usr/bin/python

"""
Defines an abstract class which handles the automatic
annotation of a document.
Returns a dictionary with the result of the annotation.
"""


class AbstractAnnotator(object):
    def process(self, doc):
        return {
            "status": "WARNING",
            "message": "this annotator doesn't do anything"
        }
