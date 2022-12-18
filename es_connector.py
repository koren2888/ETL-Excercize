from elasticsearch import Elasticsearch
from config import config


class EsConnector:
    def __init__(self, index_name):
        self.es = Elasticsearch([config["elastic.host"]])
        self.index_name = index_name

    def insert_doc(self, doc):
        self.es.index(index=self.index_name, document=doc)

    def delete_doc(self, filter_query):
        self.es.delete_by_query(index=self.index_name, body={"query": {"match": {filter_query}}})
