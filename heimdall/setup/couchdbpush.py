"""
A utility for pushing design documents to a CouchDB instance.

This is particularly useful for bootstrapping and deployment.
"""
__author__ = 'tkral'

import os

from couchdbkit import *
from couchdbkit.designer import push

if __name__ == '__main__':
    server = Server() # defaults to local CouchDB instance

    # Create the heimdall db in CouchDB
    heimdall_db = server.get_or_create_db('heimdall')

    file_dir = os.path.dirname(os.path.realpath(__file__))
    design_root_dir = os.path.join(file_dir, '_design')

    # TODO: Handle deleted design documents
    for dir in os.listdir(design_root_dir):
        design_dir = os.path.join(design_root_dir, dir)
        push(design_dir, heimdall_db)

