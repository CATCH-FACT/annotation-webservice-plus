#! /usr/bin/python
import codecs

from solr import SolrAnnotator

"""
Carries out storytype detection by looking at the most similar documents
The top 25 similar documents are retrieved from the SOLR index.
"""
MAX_NUM_RESULTS_STORYTYPES = 5

class StorytypeAnnotator(SolrAnnotator):
    def __init__(self, solr_url, evaluation_url=None):
        super(StorytypeAnnotator, self).__init__(solr_url, rows=25)

        # If we're running an experiment, ignore the test stories
        self.ignore = set()
        if evaluation_url:
            with codecs.open(evaluation_url, "r", "utf-8") as input_file:
                for line in input_file.readlines():
                    ID = line.strip().split("\t")[0]
                    self.ignore.add(ID)


    def processdocuments(self, docs, tokens):
        from collections import defaultdict

        processed = set()

        # Results by just ranking based on order of storytypes
        results_top_ranked = []
        # Results based on majority vote
        storytypes_count = defaultdict(int)

        for doc in docs:
#            if doc['identifier'] in self.ignore:
#                continue
            for storytype in doc.get('subject', []):
                storytypes_count[storytype] += 1
                if storytype not in processed:
                    results_top_ranked.append({
                        'storytype': storytype})
                    processed.add(storytype)

        if len(storytypes_count) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }

        else:
            results_majority_vote = []
            for (storytype, frequency) in sorted(storytypes_count.items(), key=lambda l: -l[1]):
                results_majority_vote.append({
                    'storytype': storytype,
                    'score': frequency
                })

            return {
                "status": "OK",
                "message": "Automatically detected storytype",
                "annotation": {
                    "storytypes": results_top_ranked[:MAX_NUM_RESULTS_STORYTYPES],
                }
            }
