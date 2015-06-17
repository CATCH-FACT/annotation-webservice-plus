# -*- coding: utf-8 -*-
#! /usr/bin/python

"""
Check if a text contains extreme content.
"""
from annotator import AbstractAnnotator
import re
import json

class ExtremeAnnotator(AbstractAnnotator):
    def __init__(self):
        super(ExtremeAnnotator, self).__init__()

    def determine_extreme(self, t, terms):
        
        extreme_score = 0
        distance_score = 0
        amount_badwords = 0
        for i in terms["not_allowed"]:
	    i = r"['\"!\?\. ]" + i + "['\"!\?\. ]" #plural?
            try:
                amount_badwords += len(re.findall(i, t))
            except:
                try:
                    amount_badwords += len(re.findall(i, " ".join(t)))
                except:
                    return None
        if (amount_badwords >= 1):
            return 100
        
        combinatory = []
        
        for i in terms["combinatory"]:
            i = r"['\"!\?\. ]" + i + "['\"!\?\. ]" #plural?            
	    for found in re.finditer(i, t):
                try:
                    for found in re.finditer(i, t):
                        combinatory.append([found.start(), found.end(), found.group(0)])
                except:
                    try:
                        for found in re.finditer(i, " ".join(t)):
                            combinatory.append([found.start(), found.end(), found.group(0)])
                    except:
                        return None
        
        distances = []
        for i in combinatory:
            extreme_score += 10 #10% per combinatory word
            for j in combinatory:
                if not (i == j):
                    if (2 <= i[0]-j[0] <= 50): #max distance of combinations
                        distances.append((i[0]-j[0]) * 5)

        if len(distances): distance_score = reduce(lambda x, y: x + y, distances) / len(distances)
        extreme_score = extreme_score + distance_score
        return extreme_score if (extreme_score <= 100) else 100
                    

    def process(self, doc):
                
        text = doc.get("text", '').strip()
        terms = json.loads(doc.get("extreme_terms", '').strip())
        
        print terms
        
        if not (terms):
            return {
                "status": "ERROR",
                "message": "No terms provided"
            }
        elif text == '':
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            tl = self.determine_extreme(text, terms);
            extreme = "ja" if tl >= 50 else "nee"

            return {
                "status": "OK",
                "message": "Automatically detected extreme text",
                "annotation": {
                    "value": extreme,
                    "score": tl
                }
            }
