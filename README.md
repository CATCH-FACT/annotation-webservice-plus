# FACT annotation web services

This repository contains the Folktales as Classifiable Texts web annotation service and a small web client to use the web services.

* **service** contains the python webservice. 
* **web** contains the simple web client.

## Python web service

### Functionality
The python web service provides:

* Extractive **summarization**, an implementation of SumBasic (Nenkova et al., 2005)
* Automatic **keyword assignment** (based on K-NN)
* Automatic **language identifcation** (based on K-NN)
* Automatic **subgenre identification** (based on K-NN)
* Automatic **named entity (location) recognition** (based on Frog)
* Automatic **named entity (other) recognition** (based on Frog)
* Automatic **extreme content detection** (based on simple profanity list)

functionality to be added:

* Automatic **folktale type identification**
* Automatic **motif identification**
* Automatic **clustering methods**
* Automatic **Literary content detection**

### Dependencies
The following python packages are required:

* [web.py](http://webpy.org/), for running the webservice
* [requests](http://docs.python-requests.org/en/latest/), for connecting to the SOLR index
* [jsonpath_rw](https://github.com/kennknowles/python-jsonpath-rw), for jsonpath expressions
* [nltk](http://www.nltk.org), for sentence segmentation and tokenization

For named entity recognition [FROG](http://ilk.uvt.nl/frog/) and its dependencies (Timbl, ucto etc.) should be installed and running as a service. See the [FROG](http://ilk.uvt.nl/frog/) for installation instructions.
Start the FROG web service at port 12345 with the following command:
`frog -S 12345 --skip=p`
The frog host and port name should be passed as parameters to the web service.

The current collection should to be indexed using [SOLR](http://lucene.apache.org/solr).
The document text should be available in the field 'text' in the index.
The location of the SOLR collection can be specified when starting the service.

### Starting the web service

The web service can be started using the following command:

`python factservice.py -solr "http://server:8080/solr/collection_name" -frog "http://froghostname:12345"`

By default the service will run on port 24681.

## Simple web client

The simple web client uses PHP, HTML, CSS and Javascript and displays a single page which uses the python web service. This code can be used as an inspiration to build an interface for semi-automatic annotation. 
