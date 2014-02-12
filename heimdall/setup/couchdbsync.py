"""
A utility for syncing design documents from a CouchDB instance.

This is particularly useful for development.
"""
__author__ = 'tkral'

import distutils.core
import os
import tempfile

from couchdbkit import *
from couchdbkit.designer import clone

if __name__ == '__main__':
    server = Server() # defaults to local CouchDB instance

    # Create the heimdall db in CouchDB
    heimdall_db = server.get_or_create_db('heimdall')

    # Get all the design documents off of the heimdall db
    design_docs = heimdall_db.all_docs(by_seq=False, params='startkey="_design/"&endkey="_design0"')

    # Clone all design documents into a temporary directory
    tmp_dir = tempfile.mkdtemp(suffix='-heimdall_sync')
    for design_doc in design_docs:
        clone(heimdall_db, design_doc['key'], os.path.join(tmp_dir, design_doc['key']))

    # Walk through the temporary directory and filter out unwanted files
    for root, dirs, files in os.walk(tmp_dir):
        for filename in files:
            if filename == '.couchapprc':
                os.remove(os.path.join(root, filename))

    # Copy the temporary directory into the working tree
    file_dir = os.path.dirname(os.path.realpath(__file__)) # heimdall/setup
    distutils.dir_util.copy_tree(tmp_dir, file_dir)
    distutils.dir_util.remove_tree(tmp_dir)

