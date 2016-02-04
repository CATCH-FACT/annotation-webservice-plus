#! /usr/bin/python

"""

REST web service for doing automatic
- language identification
- automatic summarization
- keyword extraction
- subgenre classification
- named entity recognition
- named entity location recognition
- named entity other recognition
- storytype recognition
- motif recognition

By default, starts a webservice at port 24681 (can be set with the -p switch)

Expects posting a document to be annotated to one the following urls
/language
/summary
/keywords
/subgenre
/ner
/nerlocations
/nerother
/storytype
/motif

expects the fields of the document to be posted:
    text: Full-text of the document (required),
    summary: Summary of the document (optional),
    language: Language of the document (optional),
    ...

# test with
curl http://localhost:24681/language?text=dit%20is%20een%20test

"""

import argparse
from constants import *
import web
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
from motif import MotifAnnotator

parser = argparse.ArgumentParser(
    description='''Runs the FACT language, summary, keywords, storytype, motif, wordcount and wordcountclass metadata annotator web service''')
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


class FactApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


if __name__ == "__main__":
    args = parser.parse_args()
    print "Starting webservice at port {}".format(args.p)

    mapping = {
        'language': LanguageAnnotator(args.solr),
        'keywords': KeywordsAnnotator(args.solr),
        'subgenre': SubgenreAnnotator(args.solr),
        'ner': NerAnnotator(args.frog),
	    'nerlocations': NerLocationsAnnotator(args.frog),
        'nerother': NerOtherAnnotator(args.frog),
        'summary': SummaryAnnotator(),
        'wordcount': WordcountAnnotator(),
        'wordcountclass': WordcountClassAnnotator(),
        'extreme': ExtremeAnnotator(),
        'extremebysolr': ExtremeBySolrAnnotator(args.solr),
        'storytype': StorytypeAnnotator(args.solr, args.evaluation_ids),
        'motif': MotifAnnotator(args.solr, args.evaluation_ids),
    }

    class MainHandle:
        def GET(self, name):
            return self.process(name)

        def POST(self, name):
            return self.process(name)

        def process(self, name):
            # allow requests from all domains
            web.header('Access-Control-Allow-Origin', '*')
            web.header('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT')

            if name in mapping:
                return json.dumps(mapping[name].process(web.input()))
            else:
                # unknown process
                return "Error: " + str(web.internalerror())

    urls = (
        '/(.*)', MainHandle
    )

    web.config.debug = args.debug

    app = FactApplication(urls, globals())
    app.run(port=args.p)
    
