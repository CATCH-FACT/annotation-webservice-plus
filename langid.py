#! /usr/bin/python

from solr import SolrAnnotator

"""
Carries out language detectino by looking at the most similar documents
The top 20 similar documents are retrieved from the SOLR index and
the most frequent language encountered is returned.
"""


class LanguageAnnotator(SolrAnnotator):
    def __init__(self, solr_url):
        super(LanguageAnnotator, self).__init__(solr_url, rows=10)

    def processdocuments(self, docs, tokens):
        # simply do a majority vote
        from collections import defaultdict
        r = defaultdict(int)
        for doc in docs:
            for language in doc.get('language', [])[:1]:
                r[language] += 1

        if len(r) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }
        else:
            language = sorted(r.items(), key=lambda l: -l[1])[0][0]
            return {
                "status": "OK",
                "message": "Automatically detected language",
                "annotation": {
                    "language": language,
                }
            }
