#! /usr/bin/python
# -*- coding: utf-8 -*-
'''
Created on Sep 21, 2015

@author: iwemuiser
'''

import argparse
from constants import *
import web
import requests
import json
from langid import LanguageAnnotator
from keywords import KeywordsAnnotator
from summary import SummaryAnnotator
from subgenre import SubgenreAnnotator
from wordcount import WordcountAnnotator
from wordcountclass import WordcountClassAnnotator
from extreme import ExtremeAnnotator
from extremebysolr import ExtremeBySolrAnnotator
from ner import NerAnnotator
from nerlocations import NerLocationsAnnotator
from nerother import NerOtherAnnotator
from storytype import StorytypeAnnotator
from comparison import ComparisonAnnotator
import pprint

parser = argparse.ArgumentParser(
    description='''Runs the FACT language, summary, keywords, wordcount and wordcountclass metadata annotator web service''')
parser.add_argument(
    '--debug',
    help="Sets output from the webservice to debug mode",
    action='store_const',
    const=True,
    default=False)
parser.add_argument(
    '-p',
    help="Port to run the webservice on (default: {})".format(DEFAULT_PORT),
    type=int,
    default=DEFAULT_PORT)
parser.add_argument(
    '-solr',
    help="SOLR collection url (default: {})".format(DEFAULT_SOLR_URL),
    default=DEFAULT_SOLR_URL)
parser.add_argument(
    '-frog',
    help="FROG server and port (default: {})".format(DEFAULT_FROG),
    default=DEFAULT_FROG)
parser.add_argument(
    '-evaluation_ids',
    help="File containing story IDs to ignore for evaluation (default: None)")


args = parser.parse_args()
    
mapping = {
    'comparebytext': ComparisonAnnotator(args.solr, "text"),
    'comparebymetadata': ComparisonAnnotator(args.solr, "metadata"),
}

def get_scores(model_id_to_compare):

    r = requests.post(
                "{}/select".format(DEFAULT_SOLR_URL),
                {
                    'wt': 'json',
                    'q': "modelid:" + model_id_to_compare,
                    'fq': 'collection_id:1',  # only search for similar folktales
                    'rows': 2,
                    'fl': '*,score',
                })
    doc = r.json().get('response', {}).get('docs', [])
    doc[0]["text"] = doc[0]["main_text"]
    
    bytext = mapping["comparebytext"].process(doc[0])
    bymetadata = mapping["comparebymetadata"].process(doc[0])

    return [bytext, bymetadata]


def get_all_folktale_ids():
    r = requests.post(
        "{}/select".format(DEFAULT_SOLR_URL),
        {
            'wt': 'json',
            'q': "*:*",
            'fq': 'collection_id:1',  # only search for similar folktales
            'rows': 99999,
            'fl': 'modelid',
        })
    docs = r.json().get('response', {}).get('docs', [])
#    print docs[42000:42200]
    return docs
    
if __name__ == '__main__':
    pp = pprint.PrettyPrinter(depth=6)

#    print "Starting webservice at port {}".format(args.p)

    all_folktales_by_id = get_all_folktale_ids()

    list_of_scores = {}
    count = 0
    for i in all_folktales_by_id:
        count += 1
        print count, i["modelid"]
        
        list_of_scores[i["modelid"]] = get_scores(i["modelid"])
#        get_scores(i.score)

#    pp.pprint(list_of_scores)
    
    with open('/Volumes/Data/Data/folktales_document_comparison_by_solr-2016-02-10_single.json', 'w') as outfile:
        json.dump(list_of_scores, outfile, indent=4)