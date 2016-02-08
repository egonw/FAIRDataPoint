# FAIR Data Point Service
#
# Copyright 2015 Netherlands eScience Center in collaboration with
# Dutch Techcenter for Life Sciences.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# FAIR Data Point (FDP) Service exposes the following endpoints (URL paths):
#   [ /, /doc, /doc/ ]             = Redirect to the API documentation (Swagger UI)
#   /fdp                           = returns FDP metadata
#   /catalog/{catalogID}           = returns catalog metadata (default: catalog-01)
#   /dataset/{datasetID}           = returns dataset metadata (default: breedb)
#   /distribution/{distributionID} = returns distribution metadata (default: breedb-sparql)
#
# This services makes extensive use of metadata defined by:
#   Data Catalog Vocabulary (DCAT, http://www.w3.org/TR/vocab-dcat/)
#   Dublin Core Metadata Terms (DCMI, http://dublincore.org/documents/dcmi-terms/)
#

__author__  = 'Arnold Kuzniar'
__version__ = '0.3.5'
__status__  = 'Prototype'
__license__ = 'Apache Lincense, Version 2.0'

import os
from bottle import (get, run, static_file, redirect, response, request, opt)
from metadata import FAIRGraph
from miniuri import Uri

project_dir = os.path.dirname(os.path.abspath(__file__))
#metadata_dir = os.path.join(project_dir, 'rdf_metadata/')
doc_dir = os.path.join(project_dir, 'doc/')

# set use case-specific metadata for FDP, data catalog(s) and data set(s)
host = opt.bind # host:[port] read from the command-line -b option
u = Uri(host)
u.scheme = 'http' # add scheme to host
g = FAIRGraph(u.uri)

g.setFdpMetadata(meta=dict(
      fdp_id='FDP-WUR-PB',
      catalog_ids=['catalog-01'],
      title='FAIR Data Point of the Plant Breeding Group, Wageningen UR',
      des='This FDP provides metadata on plant-specific genotype/phenotype data sets.'))

g.setCatalogMetadata(meta=dict(
   catalogs=[
     dict(catalog_id='catalog-01',
     title='Plant Breeding Data Catalog',
     des='Plant Breeding Data Catalog',
     publisher='http://orcid.org/0000-0002-4368-8058',
     issued='2015-11-24',
     modified='2015-11-24',
     dataset_ids=['breedb'])
   ]))

g.setDatasetAndDistributionMetadata(meta=dict(
   datasets=[
      dict(dataset_id='breedb',
      title='BreeDB tomato passport data',
      des='BreeDB tomato passport data',
      publisher='http://orcid.org/0000-0002-4368-8058',
      issued='2015-11-24',
      modified='2015-11-24',
      landing_page='http://www.eu-sol.wur.nl/passport',
      keywords=['BreeDB', 'Plant breeding', 'germplasm', 'passport data'],
      distributions=[
         dict(distribution_id='breedb-sparql',
            title='SPARQL endpoint for BreeDB tomato passport data',
            des='SPARQL endpoint for BreeDB tomato passport data',
            license='http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0',
            access_url='http://virtuoso.biotools.nl:8888/sparql',
            # graph_uri = 'https://www.eu-sol.wur.nl/passport', # TODO
            media_types=['text/n3', 'application/rdf+xml']
         ),
         dict(distribution_id='breedb-sqldump',
            title='SQL dump of the BreeDB tomato passport data',
            des='SQL dump of the BreeDB tomato passport data',
            license='http://rdflicense.appspot.com/rdflicense/cc-by-nc-nd3.0',
            download_url='http://virtuoso.biotools.nl:8888/DAV/home/breedb/breedb.sql',
            media_types=['application/sql']
         )
      ])
   ]))

def httpResponse(graph, uri):
   mime_type = ''
   accept_header = request.headers.get('Accept')

   if 'n3' in accept_header:
      mime_type = 'text/n3'
   elif 'rdf+xml' in accept_header:
      mime_type = 'application/rdf+xml'
   elif 'ld+json' in accept_header:
      mime_type = 'application/ld+json'
   else:
      mime_type = 'text/turtle'

   response.content_type = mime_type
   response.set_header('Allow', 'GET')  

   return graph.serialize(uri, mime_type)

# implement request handlers
@get(['/', '/doc', '/doc/'])
def defaultPage():
   redirect('/doc/index.html')

@get('/doc/<fname:path>')
def sourceDocFiles(fname):
   return static_file(fname, root=doc_dir)

@get('/fdp')
def getFdpMetadata(graph=g):
   return httpResponse(graph, graph.fdpURI())

@get('/catalog/<catalog_id>')
def getCatalogMetadata(catalog_id, graph=g):
   return httpResponse(graph, graph.catURI(catalog_id))

@get('/dataset/<dataset_id>')
def getDatasetMetadata(dataset_id, graph=g):
   return httpResponse(graph, graph.datURI(dataset_id))

@get('/distribution/<distribution_id>')
def getDistributionMetadata(distribution_id, graph=g):
   return httpResponse(graph, graph.distURI(distribution_id))

if __name__ == '__main__':
   run(server='wsgiref')
