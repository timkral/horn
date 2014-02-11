__author__ = 'tkral'

import hashlib
import json
import requests
import sys
import xmltodict

from subprocess import call, check_output

class RemoteCCollabReview:

    def __init__(self, ccollab_review_id):
        self.ccollab_review_id = ccollab_review_id

    def __calc_hash(self, ccollab_review_dict):
        review_md5 = 0

        artifacts =  ccollab_review_dict["reviews"]["review"]["artifacts"]["artifact"]
        artifacts_type = artifacts.__class__.__name__

        # Unfortunately, xmltodict doesn't handle a single element the same way as multiple
        # elements. So we have to check whether or not we have multiple elements (i.e. a list)
        if artifacts_type == 'list':
            for artifact in ccollab_review_dict["reviews"]["review"]["artifacts"]["artifact"]:
                review_md5 ^= self.__calc_artifact_hash(artifact)
        else:
            review_md5 ^= self.__calc_artifact_hash(artifacts)

        return review_md5

    def __calc_artifact_hash(self, artifact_dict):
        filename = artifact_dict["path"]
        file_content_hash = artifact_dict["md5sum"]
        return int(hashlib.md5(filename).hexdigest(), 16) ^ int(file_content_hash, 16)

    def load(self):
        ccollab_review_xml = check_output(['ccollab', 'admin', 'review-xml', self.ccollab_review_id])

        ccollab_review_dict = xmltodict.parse(ccollab_review_xml)
        ccollab_review_checksum = self.__calc_hash(ccollab_review_dict)

        ccollab_review_dict.update(category='review');
        ccollab_review_dict.update(category_sub='ccollab')
        ccollab_review_dict.update(checksum='{0:032x}'.format(ccollab_review_checksum))

        return ccollab_review_dict

if __name__ == '__main__':

    # TODO: Replace with polling system
    ccollab_review_id = sys.argv[1]
    data_store_url = 'http://127.0.0.1:5984/compliance/{0}'.format(ccollab_review_id)

    remote_ccollab_review = RemoteCCollabReview(ccollab_review_id)
    ccollab_review_dict = remote_ccollab_review.load()

    ccollab_review_phase = ccollab_review_dict["reviews"]["review"]["general"]["phase"]["#text"]
    if ccollab_review_phase == 'Completed':
        put_response = requests.put(data_store_url, data=json.dumps(ccollab_review_dict, sort_keys=True))
        print json.dumps(put_response.json(), sort_keys=True)
    else:
        print 'Skipping review {0} as it is in the {1} phase'.format(ccollab_review_id, ccollab_review_phase)