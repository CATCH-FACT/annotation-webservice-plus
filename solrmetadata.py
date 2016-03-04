#! /usr/bin/python
'''
Created on Sep 22, 2015

Makes search query out of items based on metadata list and returns a list of scores

@author: iwemuiser
'''

from annotator import AbstractAnnotator
import requests
from jsonpath_rw import parse
from constants import FIELD_TEXT

"""

Annotator which searches the SOLR index for similar documents
and suggests annotations based on these similar documents.

"""
STOPWORDS = set(["de", "het", "en", "een", "er", "die", "dit", "van", "te", "dat", "in", "is", "zijn", "was",
                 "op", "aan", "met", "als", "voor", "maar", "om", "dan", "wat", "zo", "door", "over", "bij", "tot",
                 "der", "daar", "naar", "deze", "nog", "omdat", "iets", "al", "dus", "hier", "wordt", "geworden",
                 "worden", "na", "reeds"])

metadatas_to_query = {
            "title":            False,
            "subject":          False,
            "creator":          False,
            "contributor":      False,
            "collector":        False,
            "language":         False,
            "source":           False,
            "date":             False,
            "format":           False,
            "type":             False,
            "subgenre":         False,
            "motif":            False,
            "literary":         False,
            "extreme":          False,
            "named_entity":     False,
            "named_entity_location": False,
            "place_of_action":  False,
            "corpus":           False,
            "tag":              1,
            "text_length":      False,
            "text_length_group":False,
            "location":         False,
            "sublocality":      False,
            "locality":         False,
            "administrative_area_level_1": False,
            "administrative_area_level_2": False,
            "administrative_area_level_3": False,
            "country":          False,
            "text":             False};

#original score schema
metadatas_to_query = {
            "title":            1,
            "subject":          200,
            "creator":          False,
            "contributor":      False,
            "collector":        False,
            "language":         False,
            "source":           False,
            "date":             False,
            "format":           False,
            "type":             1,
            "subgenre":         1,
            "motif":            1,
            "literary":         1,
            "extreme":          1,
            "named_entity":     1,
            "named_entity_location": 1,
            "place_of_action":  1,
            "corpus":           False,
            "tag":              1,
            "text_length":      False,
            "text_length_group":1,
            "location":         False,
            "sublocality":      False,
            "locality":         False,
            "administrative_area_level_1": False,
            "administrative_area_level_2": False,
            "administrative_area_level_3": False,
            "country":          False,
            "text":             False};

#website score schema
metadatas_to_query = {
            "title":            False,
            "subject":          20,
            "creator":          False,
            "contributor":      False,
            "collector":        False,
            "language":         False,
            "source":           False,
            "date":             False,
            "format":           False,
            "type":             False,
            "subgenre":         1,
            "motif":            1,
            "literary":         1,
            "extreme":          1,
            "named_entity":     1,
            "named_entity_location": 1,
            "place_of_action":  1,
            "corpus":           False,
            "tag":              0.7,
            "word_count":       False,
            "word_count_group": False,
            "location":         False,
            "sublocality":      False,
            "locality":         False,
            "administrative_area_level_1": False,
            "administrative_area_level_2": False,
            "administrative_area_level_3": False,
            "country":          False,
            "text":             False};


class SolrplusAnnotator(AbstractAnnotator):
    def __init__(self, solr_url, rows, style):
        super(SolrplusAnnotator, self).__init__()
        self.solr_url = solr_url
        self.rows = rows
        self.style = style

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
                if i['text'] not in STOPWORDS and len(i['text']) > 1:
                    tokens.append(i['text'])
            break
        return tokens

    def generate_item_query(self, doc, metadatas_to_query):
        or_pre_query = []
        for index in doc:
            value = doc[index]
            for metaindex in metadatas_to_query:
                metavalue = metadatas_to_query[metaindex]
                if metaindex == index and metavalue:
                    if isinstance(value, list):
                        for subindex in value:
                            or_pre_query.append(index + ':"' + subindex + '"^' + str(metavalue));
                    else:
                        or_pre_query.push(index + ':' + value + '"');
        return "(" + " OR ".join(or_pre_query) + ") AND !modelid:" + doc.get("modelid", '')
    

    """
    Builds a lucene OR query using the given tokens
    """
    def buildquery(self, tokens, andnot):
        tokens = tokens[:450]  # longer queries have no results in solr
        query = "{!lucene q.op=OR df=" + FIELD_TEXT + "} " + " ".join(tokens)
        if (andnot): 
            return query + " AND !modelid:" + andnot
        else:
            return query

    """
    Retrieves documents similar to the list of tokens
    Returns an array of SOLR documents (or an empty list)
    """
    def get_similar(self, query):
        if len(query) > 0:
            r = requests.post(
                "{}/select".format(self.solr_url),
                {
                    'wt': 'json',
                    'q': query,
                    'fq': 'collection_id:1',  # only search for similar folktales
                    'rows': self.rows,
                    'fl': '*,score',
                })
            return r.json().get('response', {}).get('docs', [])
        else:
            return []

    def processdocuments(self, docs, tokens):
        raise Exception("Should be implemented in subclass")

    def process(self, doc):
        if self.style == "text":
            return self.processbytext(doc)
        elif self.style == "metadata":
            return self.processbymetadata(doc)

    def processbymetadata(self, doc):

        query =  self.generate_item_query(doc, metadatas_to_query)
    
#        print query
        
        if len(doc.get("text", '')) == 0:
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            return self.processdocuments(self.get_similar(query), "")
    
    def processbytext(self, doc):

        text = doc.get("text", '')
        #to leave one out
        modelid = doc.get("modelid", '')
        
#        print modelid
        
        tokens = self.tokenize(text)

        query = self.buildquery(tokens, modelid)
        
        if len(tokens) == 0:
            return {
                "status": "ERROR",
                "message": "No text provided"
            }
        else:
            return self.processdocuments(self.get_similar(query), tokens)

