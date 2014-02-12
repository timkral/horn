"""
A class for verifying an environment to run Heimdall
"""
__author__ = 'tkral'

import os
import sys

from heimdall.setup.heimdallconfig import HeimdallConfig
from subprocess import check_output

class HeimdallVerifier:

    def __init__(self, config_dir):
        self.config_dir = config_dir

    def verify(self):
        sys.stdout.write('Verifying heimdall config exists...')
        config = HeimdallConfig(self.config_dir)
        self.__verify_bool(os.path.exists(config.config_file))

        sys.stdout.write('Verifying git version >= 1.7...')
        git_version_output = check_output(['git', '--version'])
        git_version_parsed = git_version_output.split()
        git_version_number = git_version_parsed[2]
        sys.stdout.write('[{0}]'.format(git_version_number))
        self.__verify_bool(git_version_number > '1.7')

        sys.stdout.write('Verifying ccollab version >= v6.5...')
        ccollab_version_output = check_output(['ccollab', '--version'])
        ccollab_version_parsed = ccollab_version_output.split()
        ccollab_version_number = ccollab_version_parsed[1]
        sys.stdout.write('[{0}]'.format(ccollab_version_number))
        self.__verify_bool(ccollab_version_number > 'v6.5')

        # TODO: Verify connection to couch_db_instance
        # TODO: Verify connection to git_repository_instance
        # TODO: Verify connection using ccollab

    def __verify_bool(self, bool):
        if bool == True:
            print '[OK]'
        else:
            print '[ERROR]'