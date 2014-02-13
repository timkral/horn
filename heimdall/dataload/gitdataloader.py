__author__ = 'tkral'

import hashlib
import json
import os
import requests
import sys

from subprocess import call, check_output

class GitCommit:

    def __init__(self, remote_git_repo, local_git_repo, sha1):
        self.remote_git_repo = remote_git_repo
        self.local_git_repo = local_git_repo
        self.sha1 = sha1

    def load(self):
        get_response = requests.get(self.remote_git_repo.remote_api_url)

        git_commit_dict = get_response.json()
        git_commit_checksum = self.__calc_hash()

        git_commit_dict.update(category='commit')
        git_commit_dict.update(category_sub='git')
        git_commit_dict.update(checksum='{0:032x}'.format(git_commit_checksum))

        return git_commit_dict

    def __calc_hash(self):
        commit_md5 = 0
        for filename in self.__list_diff_filenames():
            commit_md5 ^= self.__calc_file_hash(filename)

        return commit_md5

    def __calc_file_hash(self, filename):
        # Check if the filename exists at the particular git revision
        # This exits with zero when there's no error
        file_exists = self.local_git_repo.exec_cmd(['cat-file', '-e', '{0}:{1}'.format(self.sha1, filename)], suppress_error=True)

        if file_exists == 0:
            file_content = self.local_git_repo.exec_cmd(['show', '{0}:{1}'.format(self.sha1, filename)], return_output=True)
            file_content_hash = hashlib.md5(file_content).hexdigest()
        else:
            # In the case where the file is missing from the revision (which may just be a deleted file),
            # return the md5 hash of a null file
            file_content_hash = hashlib.md5().hexdigest()

        filename_hash = hashlib.md5(filename).hexdigest()
#        print'Calculated file {0}: {1} ^ {2}'.format(filename, filename_hash, file_content_hash)
        return int(filename_hash, 16) ^ int(file_content_hash, 16)

    def __list_diff_filenames(self):
        # Execute a git diff with the --numstat option. This produces a machine readable list of changed files in the diff
        git_diff_output = self.local_git_repo.exec_cmd(['diff', '--numstat', '{0}~1'.format(self.sha1), self.sha1], return_output=True)
        git_diff_output_parsed = git_diff_output.splitlines()

        diff_filenames = []
        for git_diff in git_diff_output_parsed:
            git_diff_parsed = git_diff.split()

            diff_additions = git_diff_parsed[0]
            diff_deletions = git_diff_parsed[1]
            filename = git_diff_parsed[2]

            # Skip all binary files (which do not report diff stats)
            if diff_additions == '-' or diff_deletions == '-':
                print 'Skipping binary file {0}'.format(filename)
            else:
                diff_filenames.append(filename)

        return diff_filenames

class LocalGitRepo:

    def __init__(self, config):
        self.local_work_tree = os.path.join(config.config_dict['git_repo_local_dir'], config.config_dict['git_repo_org'], config.config_dict['git_repo_name'])
        if not os.path.exists(self.local_work_tree):
            os.makedirs(self.local_work_tree)

        # If the local git dif does not exist then we don't have an initialized
        # git repository. So initialize one.
        self.local_git_dir = os.path.join(self.local_work_tree, '.git')
        if not os.path.exists(self.local_git_dir):
            # Create a special environment for executing the `git init` command
            # this will set the GIT_DIR env variable to ensure that the .git/
            # directory is placed there
            git_init_env = os.environ.copy()
            git_init_env['GIT_DIR'] = self.local_git_dir
            call(['git', '--work-tree={0}'.format(self.local_work_tree), 'init'], env=git_init_env)

            self.exec_cmd(['remote', 'add', 'origin', '{0}/{1}/{2}.git'.format(config.config_dict['git_repo_instance'], config.config_dict['git_repo_org'], config.config_dict['git_repo_name'])])

        self.git_branch = config.config_dict['git_repo_branch']

        # Execute a pull
        self.exec_cmd(['pull', 'origin'])
        # Checkout the configurated git branch
        self.exec_cmd(['checkout', self.git_branch])

    def exec_cmd(self, arg_list, return_output=False, suppress_error=False):
        git_cmd_list = ['git', '--git-dir={0}'.format(self.local_git_dir), '--work-tree={0}'.format(self.local_work_tree)] + arg_list

        # TODO: Write any error message out to log file
        with open(os.devnull, "w") as fnull:
            if return_output:
                return check_output(git_cmd_list, stderr=fnull if suppress_error else sys.stderr)
            else:
                return call(git_cmd_list, stderr=fnull if suppress_error else sys.stderr)

class RemoteGitRepo:

    def __init__(self, config):
                # Build the remote git API url from the Heimdall configuration (see HeimdallConfig class)
        self.remote_api_url = '{0}/api/v3/repos/{1}/{2}'.format(config.config_dict['git_repo_instance'], config.config_dict['git_repo_org'], config.config_dict['git_repo_name'])