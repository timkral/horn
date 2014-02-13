"""
A class for storing and retrieving Heimdall configuration
"""
__author__ = 'tkral'

import json
import os

class HeimdallConfig:

    def __init__(self, config_dir, config_filename='.heimdall.config'):
        self.config_file = os.path.join(config_dir, config_filename)

    def exists(self):
        return os.path.exists(self.config_file)

    def init(self):
        curr_config_dict = {}
        if self.exists():
            curr_config_dict = self.__load()

        # If a configuration already exists then use the current
        # configuration as default values
        self.config_dict = {}
        self.config_dict.update(couch_db_instance='{0}'.format(self.__config_ask('CouchDB instance', curr_config_dict.get('couch_db_instance', 'http://127.0.0.1:5984'))))
        self.config_dict.update(git_repo_instance='{0}'.format(self.__config_ask('Git repository instance', curr_config_dict.get('git_repo_instance', 'https://git.soma.salesforce.com'))))
        self.config_dict.update(git_repo_org='{0}'.format(self.__config_ask('Git repository org', curr_config_dict.get('git_repo_org', ''))))
        self.config_dict.update(git_repo_name='{0}'.format(self.__config_ask('Git repository name', curr_config_dict.get('git_repo_name', ''))))
        self.config_dict.update(git_repo_branch='{0}'.format(self.__config_ask('Git repository branch', curr_config_dict.get('git_repo_branch', 'master'))))
        self.config_dict.update(git_repo_access_token='{0}'.format(self.__config_ask('Git repository access token', curr_config_dict.get('git_repo_access_token', ''), required=False)))
        self.config_dict.update(git_repo_local_dir='{0}'.format(self.__config_ask('Git repository local directory', curr_config_dict.get('git_repo_local_dir', os.path.join(os.path.expanduser('~'), '.heimdall')))))

        with open(self.config_file, 'w') as f:
            json.dump(self.config_dict, f)

    def __config_ask(self, message, default_value, required=True):
        # TODO: Raise exception is len(value) == 0 and required and default_value not present
        value = raw_input('{0}[{1}]: '.format(message, default_value))
        return value if len(value) > 0 else default_value

    def load(self):
        self.config_dict = self.__load()

    def __load(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def purge(self):
        if self.exists():
            os.remove(self.config_file)