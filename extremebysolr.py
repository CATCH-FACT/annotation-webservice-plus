#! /usr/bin/python

from solr import SolrAnnotator

"""
Carries out subgenre detection by looking at the most similar documents
The top 20 similar documents are retrieved from the SOLR index and
the most frequent subgenre encountered is returned.
"""

class ExtremeBySolrAnnotator(SolrAnnotator):
    def __init__(self, solr_url):
        super(ExtremeBySolrAnnotator, self).__init__(solr_url, rows=4)

    def processdocuments(self, docs, tokens):
        # simply do a majority vote
        from collections import defaultdict
        r = defaultdict(int)
        for doc in docs:
            r[doc.get('extreme')] += 1

        if len(r) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }
        else:
            extreme = sorted(r.items(), key=lambda l: -l[1])[0][0]
            return {
                "status": "OK",
                "message": "Automatically detected extreme text",
                "annotation": {
                    "value": extreme,
                }
            }

