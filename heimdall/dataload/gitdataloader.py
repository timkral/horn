__author__ = 'tkral'

import hashlib
import json
import os
import requests
import sys

from subprocess import call, check_output

class LocalGitCommit:

    def __init__(self, local_work_tree, git_commit_sha1):
        self.local_work_tree = local_work_tree
        self.local_git_dir = os.path.join(local_work_tree, '.git')
        self.git_commit_sha1 = git_commit_sha1

    def calc_hash(self):
        commit_md5 = 0
        for filename in self.__list_diff_filenames():
            commit_md5 ^= self.__calc_file_hash(filename)

        return commit_md5

    def __calc_file_hash(self, filename):
        # Check if the filename exists at the particular git revision
        # This exits with zero when there's no error
        # TODO: Write any error message out to log file
        with open(os.devnull, "w") as fnull:
            file_exists = call(['git', '--git-dir={0}'.format(self.local_git_dir), '--work-tree={0}'.format(self.local_work_tree), 'cat-file', '-e', '{0}:{1}'.format(self.git_commit_sha1, filename)], stderr=fnull)

        if file_exists == 0:
            file_content = check_output(['git', '--git-dir={0}'.format(self.local_git_dir), '--work-tree={0}'.format(self.local_work_tree), 'show', '{0}:{1}'.format(self.git_commit_sha1, filename)])
            file_content_hash = hashlib.md5(file_content).hexdigest()
        else:
            # In the case where the file is missing from the revision (which may just be a deleted file),
            # return the md5 hash of a null file
            file_content_hash = hashlib.md5().hexdigest()

        filename_hash = hashlib.md5(filename).hexdigest()
#        print'Calculated file {0}: {1} ^ {2}'.format(filename, filename_hash, file_content_hash)
        return int(filename_hash, 16) ^ int(file_content_hash, 16)

    def __list_diff_filenames(self):
        git_diff_output = check_output(['git', '--git-dir={0}'.format(self.local_git_dir), '--work-tree={0}'.format(self.local_work_tree), 'diff', '--numstat', '{0}~1'.format(self.git_commit_sha1), self.git_commit_sha1])
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

class RemoteGitCommit:

    def __init__(self, remote_api_url, access_token, local_git_commit):
        self.remote_api_url = remote_api_url
        self.access_token = access_token
        self.local_git_commit = local_git_commit

    def load(self):
        get_response = requests.get('{0}/commits/{1}?access_token={2}'.format(self.remote_api_url, self.local_git_commit.git_commit_sha1, self.access_token))

        git_commit_dict = get_response.json()
        git_commit_checksum = self.local_git_commit.calc_hash()

        git_commit_dict.update(category='commit')
        git_commit_dict.update(category_sub='git')
        git_commit_dict.update(checksum='{0:032x}'.format(git_commit_checksum))

        return git_commit_dict

if __name__ == '__main__':

    # TODO: Replace with polling system
    git_commit_sha1 = sys.argv[1]
    data_store_url = 'http://127.0.0.1:5984/heimdall/{0}'.format(git_commit_sha1)

    local_git_commit = LocalGitCommit('/home/tkral/dev/raiden/raiden-net', git_commit_sha1)
    remote_git_commit = RemoteGitCommit('https://{0}/api/v3/repos/{1}/{2}'.format('git.soma.salesforce.com', 'raiden', 'raiden-net'), '0d9250a720b60451eddfbb54583605376fb1f1dd', local_git_commit)
    git_commit_dict = remote_git_commit.load()

    put_response = requests.put(data_store_url, data=json.dumps(git_commit_dict, sort_keys=True))
    print json.dumps(put_response.json(), sort_keys=True)