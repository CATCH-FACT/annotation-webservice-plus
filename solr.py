#! /usr/bin/python

from annotator import AbstractAnnotator
import requests
from jsonpath_rw import parse
from constants import FIELD_TEXT

"""

Annotator which searches the SOLR index for similar documents
and suggests annotations based on these similar documents.

"""

class SolrAnnotator(AbstractAnnotator):
    def __init__(self, solr_url, rows):
        super(SolrAnnotator, self).__init__()
        self.solr_url = solr_url
        self.rows = rows

    """
    Tokenizes the text using the analyzer used for
    the document text.
    Returns an array of tokens 
    """
    def tokenize(self, text):
        # use SOLR to analyse the text
        r = requests.post(
            "{}/analysis/field".format(self.solr_url),
            {
                'wt': 'json',
                'analysis.fieldname': FIELD_TEXT,
                'analysis.fieldvalue': text
            })

        path_expr = parse('analysis.field_names.*.index')
        tokens = []
        for match in path_expr.find(r.json()):
            for i in match.value[-1]:
                tokens.append(i['text'])
            break
        return tokens

    """
    Builds a lucene OR query using the given tokens
    """
    def buildquery(self, tokens):
        return "{!lucene q.op=OR df=" + FIELD_TEXT + "} " + " ".join(tokens)

    """
    Retrieves documents similar to the list of tokens
    Returns an array of SOLR documents (or an empty list)
    """
    def get_similar(self, tokens):
        if len(tokens) > 0:
            r = requests.post(
                "{}/select".format(self.solr_url),
                {
                    'wt': 'json',
                    'q': self.buildquery(tokens),
                    'fq': 'collection_id:1',  # only search for similar folktales
                    'rows': self.rows
                })
            return r.json().get('response', {}).get('docs', [])
        else:
            return []

    def processdocuments(self, docs, tokens):
        raise Exception("Should be implemented in subclass")

    def process(self, doc):
        text = doc.get("text", '')
        tokens = self.tokenize(text)

        if len(tokens) == 0:
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            return self.processdocuments(self.get_similar(tokens), tokens)

