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

        config_dict.update(couch_db_instance='{0}'.format(self.__config_ask('CouchDB instance', default_value='http://127.0.0.1:5984')))
        config_dict.update(git_repo_instance='{0}'.format(self.__config_ask('Git repository instance', default_value='https://git.soma.salesforce.com')))
        config_dict.update(git_repo_org='{0}'.format(self.__config_ask('Git repository org')))
        config_dict.update(git_repo_name='{0}'.format(self.__config_ask('Git repository name')))
        config_dict.update(git_repo_branch='{0}'.format(self.__config_ask('Git repository branch', default_value='master')))
        config_dict.update(git_repo_access_token='{0}'.format(self.__config_ask('Git repository access token', required=False)))
        config_dict.update(git_repo_local_dir='{0}'.format(self.__config_ask('Git repository local directory', default_value=os.path.join(os.path.expanduser('~'), '.heimdall'))))

        with open(self.config_file, 'w') as f:
            json.dump(config_dict, f)

    def __config_ask(self, message, required=True, default_value=''):
        # TODO: Raise exception is len(value) == 0 and required and default_value not present
        value = raw_input('{0}[{1}]: '.format(message, default_value))
        return value if len(value) > 0 else default_value

    def load(self):
        with open(self.config_file, 'r') as f:
            self.config_dict = json.load(f)