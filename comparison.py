#! /usr/bin/python
'''
Created on Sep 22, 2015

@author: iwemuiser
'''

from solrmetadata import SolrplusAnnotator

"""
Carries out subgenre detection by looking at the most similar documents
The top 20 similar documents are retrieved from the SOLR index and
the most frequent subgenre encountered is returned.
"""


class ComparisonAnnotator(SolrplusAnnotator):
    def __init__(self, solr_url, style="text"):
        self.rows = 1
        self.style = style
        super(ComparisonAnnotator, self).__init__(solr_url, self.rows, self.style)

    def processdocuments(self, docs, tokens):
        # simply do a majority vote
        total_score = 0
        highest_score = 0
        scores = []
        modelid = ''
        average_score= 0
        from collections import defaultdict
#        r = defaultdict(int)
        for doc in docs:
#            modelid = doc["modelid"]
            score = doc["score"]
            total_score += score
            scores.append(score)
            highest_score = score if score > highest_score else highest_score

        
        if len(scores) > 0:
            average_score = total_score / len(scores)
        
        return {
#            "status": "OK",
#            "message": "Similar document scores",
#            "modelid": modelid,
            self.style: {
                "cumulative_score": total_score,
                "high_score": highest_score,
                "average_score": average_score,
                "all_scores": scores
            }
        }