#! /usr/bin/python
import codecs

from solr import SolrAnnotator

"""
Carries out motif detection by looking at the most similar documents
The top 25 similar documents are retrieved from the SOLR index.
"""
MAX_NUM_RESULTS_MOTIFS = 5

class MotifAnnotator(SolrAnnotator):
    def __init__(self, solr_url, evaluation_url=None):
        super(MotifAnnotator, self).__init__(solr_url, rows=25)

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

        # Results by just ranking based on order of motifs
        results_top_ranked = []
        # Results based on majority vote
        motif_count = defaultdict(int)

        for doc in docs:
#            if doc['identifier'] in self.ignore:
#                continue
            for motif in doc.get('motif', []):
                motif_count[motif] += 1
                if motif not in processed:
                    results_top_ranked.append({
                        'motif': motif})
                    processed.add(motif)

        if len(motif_count) == 0:
            return {
                "status": "ERROR",
                "message": "Could not determine similiar documents"
            }

        else:
            results_majority_vote = []
            for (motif, frequency) in sorted(motif_count.items(), key=lambda l: -l[1]):
                results_majority_vote.append({
                    'motif': motif,
                    'score': frequency
                })

            return {
                "status": "OK",
                "message": "Automatically detected motif",
                "annotation": {
                    "motifs": results_top_ranked[:MAX_NUM_RESULTS_MOTIFS],
                }
            }
