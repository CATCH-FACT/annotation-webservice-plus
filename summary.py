#! /usr/bin/python

from __future__ import division
from annotator import AbstractAnnotator

from nltk.tokenize import sent_tokenize, word_tokenize
from collections import defaultdict
import string

"""
Implements SUM Basic for summarization.

Returns a scored list of sentences (the most valuable sentence for
summarization receives the highest score).

Nenkova, A., & Vanderwende, L. (2005).
The impact of frequency on summarization.
Microsoft Research, Redmond, Washington, Tech. Rep. MSR-TR-2005-101.
Retrieved from http://www.cs.bgu.ac.il/~elhadad/nlp09/sumbasic.pdf
"""


class SummaryAnnotator(AbstractAnnotator):
    def __init__(self):
        super(SummaryAnnotator, self).__init__()
        # import nltk.data
        # self.sent_detector = nltk.data.load('tokenizers/punkt/dutch.pickle')
        from nltk.corpus import stopwords
        self.stop = stopwords.words('dutch') + list(string.punctuation)

    def process(self, doc):
        text = doc.get("text", '').strip()

        if text == '':
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            # extract tokens and sentences
            # sentences = self.sent_detector.tokenize(text)
            # get the tokens from each sentence

            sentences = sent_tokenize(text)

            sentence_tokens = []
            for sentence in sentences:
                sentence_tokens.append(
                    [w.lower() for w in word_tokenize(sentence) if w not in self.stop]
                )

            token_counts = defaultdict(int)
            for tokens in sentence_tokens:
                for t in tokens:
                    token_counts[t] += 1

            # step 1: calculate probability over words
            p_w = {}
            total = sum(token_counts.values())
            for (token, count) in token_counts.items():
                p_w[token] = count / total

            sentence_weight = {}  # idx -> weight
            for (idx, _) in enumerate(sentence_tokens):
                sentence_weight[idx] = 0

            sentence_score = {}
            score = len(sentences)
            while len(sentence_weight) > 0:
                # step 2: calculate sentence weight
                for idx in sentence_weight:
                    sentence_weight[idx] = 0
                    tokens = sentence_tokens[idx]
                    if len(tokens) > 0:
                        for t in tokens:
                            sentence_weight[idx] += p_w[t]
                        sentence_weight[idx] /= len(tokens)

                # step 3: pick best scoring sentence that contains highest
                # probability word
                best_word = sorted(p_w.items(), key=lambda l: -l[1])[0][0]

                ranked_sentences = sorted([
                    (idx, best_word in sentence_tokens[idx], s)
                    for(idx, s) in sentence_weight.items()
                ], key=lambda l: (-l[1], -l[2]))

                if len(ranked_sentences) > 0:
                    idx = ranked_sentences[0][0]

                    sentence_score[idx] = score
                    score -= 1
                    del sentence_weight[idx]
                    # step 4:
                    for word in set(sentence_tokens[idx]):
                        p_w[word] *= p_w[word]
                else:
                    # apparently, there are no sentences left with this word
                    p_w[best_word] = 0

            result = [
                {
                    'idx': i,
                    'sentence': sentence,
                    'score': sentence_score[i]
                } for (i, sentence) in enumerate(sentences)
            ]

            # return the selected_sentences
            return {
                "status": "OK",
                "message": "Automatically created summary",
                "annotation": {
                    "summary": result,
                }
            }
