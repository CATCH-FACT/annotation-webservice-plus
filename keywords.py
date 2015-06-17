#! /usr/bin/python

from solr import SolrAnnotator

"""
Searches for (at most 20) similar documents and returns
keywords that appear in many (at least 4) similar documents or
keywords that also appear literally in this text
"""


class KeywordsAnnotator(SolrAnnotator):
    def __init__(self, solr_url):
        super(KeywordsAnnotator, self).__init__(solr_url, rows=20)

    def processdocuments(self, docs, tokens):
        # simply do a majority vote
        from collections import defaultdict
        r = defaultdict(int)
        for doc in docs:
            for tag in doc.get('tags', []):
                r[tag] += 1

        if len(r) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }
        else:
            toks = set(tokens)
            kk = []  # list of (term, frequency, in_text)
            for (term, frequency) in r.items():
                in_text = term.lower() in toks
                if frequency > 3 or in_text:
                    kk.append((term, frequency, in_text))

            # first sort by in_text, then by descending frequency
            kk = sorted(kk, key=lambda l: (-l[2], -l[1]))

            result = [
                {
                    'keyword': term,
                    'score': 100 if it else 10
                } for (term, frequency, it) in kk
            ]

            return {
                "status": "OK",
                "message": "Automatically detected keywords",
                "annotation": {
                    "keywords": result,
                }
            }
