"""
A class for verifying an environment to run Heimdall
"""
__author__ = 'tkral'

import requests
import sys

from heimdall.dataload.couchdbclient import CouchDBClient
from heimdall.dataload.gitdataloader import RemoteGitRepo
from subprocess import check_output

class HeimdallVerifier:

    def __init__(self, config):
        self.config = config

    def verify(self):
        self.__verify_config_exists()
        self.__verify_config_loading()
        self.__verify_git_version('1.7')
        self.__verify_ccollab_version('v6.5')
        self.__verify_couchdb_connection()
        self.__verify_git_connection()

        # TODO: Verify connection using ccollab

    def __verify_bool(self, bool):
        if bool == True:
            print '[OK]'
        else:
            print '[ERROR]'

    def __verify_ccollab_version(self, expected_ccollab_version):
        sys.stdout.write('Verifying ccollab version >= {0}...'.format(expected_ccollab_version))
        ccollab_version_output = check_output(['ccollab', '--version'])
        ccollab_version_parsed = ccollab_version_output.split()
        ccollab_version_number = ccollab_version_parsed[1]
        sys.stdout.write('[{0}]'.format(ccollab_version_number))
        self.__verify_bool(ccollab_version_number > expected_ccollab_version)

    def __verify_config_exists(self):
        sys.stdout.write('Verifying heimdall configuration exists...')
        self.__verify_bool(self.config.exists())

    def __verify_config_loading(self):
        sys.stdout.write('Verifying heimdall configuration loading...')
        self.config_loaded = False
        if not self.config.exists():
            print '[SKIP]'
        else:
            try:
                self.config.load()
                self.config_loaded = True
            except Exception as e:
                pass

            self.__verify_bool(self.config_loaded)

    def __verify_couchdb_connection(self):
        sys.stdout.write('Verifying CouchDB connection...')
        if not self.config_loaded:
            print '[SKIP]'
        else:
            try:
                # At initialization, the CouchDBClient attempts to
                # get a handle to the heimdall data store. So if this
                # is successful, we're good. Otherwise, we're bad.
                CouchDBClient(self.config)
                print '[OK]'
            except Exception as e:
                print '[ERROR]'

    def __verify_git_connection(self):
        sys.stdout.write('Verifying remote git connection...')
        if not self.config_loaded:
            print '[SKIP]'
        else:
            remote_git_repo = RemoteGitRepo(self.config)
            get_response = requests.get(remote_git_repo.remote_api_url)
            if get_response.status_code != 200:
                print '[ERROR]'
            else:
                get_response_dict = get_response.json()
                if 'Not Found' in get_response_dict.values():
                    print '[ERROR]'
                else:
                    print '[OK]'

    def __verify_git_version(self, expected_git_version):
        sys.stdout.write('Verifying git version >= {0}...'.format(expected_git_version))
        git_version_output = check_output(['git', '--version'])
        git_version_parsed = git_version_output.split()
        git_version_number = git_version_parsed[2]
        sys.stdout.write('[{0}]'.format(git_version_number))
        self.__verify_bool(git_version_number > expected_git_version)