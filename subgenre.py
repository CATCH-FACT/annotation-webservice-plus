#! /usr/bin/python

from solr import SolrAnnotator

"""
Carries out subgenre detection by looking at the most similar documents
The top 20 similar documents are retrieved from the SOLR index and
the most frequent subgenre encountered is returned.
"""


class SubgenreAnnotator(SolrAnnotator):
    def __init__(self, solr_url):
        super(SubgenreAnnotator, self).__init__(solr_url, rows=20)

    def processdocuments(self, docs, tokens):
        # simply do a majority vote
        from collections import defaultdict
        r = defaultdict(int)
        for doc in docs:
            for subgenre in doc.get('subgenre', [])[:1]:
                r[subgenre] += 1

        if len(r) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }
        else:
            subgenre = sorted(r.items(), key=lambda l: -l[1])[0][0]
            return {
                "status": "OK",
                "message": "Automatically detected subgenre",
                "annotation": {
                    "subgenre": subgenre,
                }
            }
