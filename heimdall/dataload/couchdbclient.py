"""
A CouchDB client for pushing and syncing design documents.
"""
__author__ = 'tkral'

import distutils.core
import json
import os
import requests
import tempfile

from couchdbkit import *
from couchdbkit.designer import clone, push

class CouchDBClient:

    def __init__(self, config):
        self.server = Server(uri=config.config_dict['couch_db_instance'])
        self.heimdall_db = self.server.get_or_create_db('heimdall')
        self.file_dir = os.path.dirname(os.path.realpath(__file__))

    def load_doc(self, doc_id, doc_dict):
        # TODO: Should we use the native couchdbkit to do this?
        put_response = requests.put('{0}/heimdall/{1}'.format(self.server.uri, doc_id), data=json.dumps(doc_dict, sort_keys=True))
        return put_response.json()

    def push(self):
        design_root_dir = os.path.join(self.file_dir, '_design')

        # TODO: Handle deleted design documents
        for dir in os.listdir(design_root_dir):
            design_dir = os.path.join(design_root_dir, dir)
            push(design_dir, self.heimdall_db)

    def sync(self):
        # Get all the design documents off of the heimdall db
        design_docs = self.heimdall_db.all_docs(by_seq=False, params='startkey="_design/"&endkey="_design0"')

        # Clone all design documents into a temporary directory
        tmp_dir = tempfile.mkdtemp(suffix='-heimdall_sync')
        for design_doc in design_docs:
            clone(self.heimdall_db, design_doc['key'], os.path.join(tmp_dir, design_doc['key']))

        # Walk through the temporary directory and filter out unwanted files
        for root, dirs, files in os.walk(tmp_dir):
            for filename in files:
                if filename == '.couchapprc':
                    os.remove(os.path.join(root, filename))

        # Copy the temporary directory into the working tree
        distutils.dir_util.copy_tree(tmp_dir, self.file_dir)
        distutils.dir_util.remove_tree(tmp_dir)