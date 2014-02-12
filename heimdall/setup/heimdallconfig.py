"""
A class for storing and retrieving Heimdall configuration
"""
__author__ = 'tkral'

import json
import os

class HeimdallConfig:

    def __init__(self, config_dir, config_filename='.heimdall.config'):
        self.config_file = os.path.join(config_dir, config_filename)

    def init(self):
        config_dict = {}

        couch_db_instance = raw_input('CouchDB instance[http://127.0.0.1:5984]: ')
        if len(couch_db_instance) == 0:
            couch_db_instance = 'http://127.0.0.1:5984'
        config_dict.update(couch_db_instance='{0}'.format(couch_db_instance))

        git_repository_instance = raw_input('Git repository instance[]: ')
        config_dict.update(git_repository_instance='{0}'.format(git_repository_instance))

        git_repository_branch = raw_input('Git repository branch[master]: ')
        if len(git_repository_branch) == 0:
            git_repository_branch = 'master'
        config_dict.update(git_repository_branch='{0}'.format(git_repository_branch))

        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f)


    def load(self):
        with open(self.config_file, 'r') as f:
            self.config_dict = json.load(f)