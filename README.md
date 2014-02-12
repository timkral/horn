Heimdall
=========

Heimdall is a build system service that checks for compliant commits to a git repository. It is licensed under the BSD-3 Clause license.

Installation
------------

At a high level, Heimdall requires that the following be installed:
* python (>= version 2.7)
* CouchDB (>= version 1.2)
* git (>= version 1.7)
* ccollab command line tool (>= version 6.5)

###Python Installation###
In order to run Heimdall, one will need the following Python modules:
* [Couchdbkit Module]
* [Requests Module]
* [xmltodict Module]

###CouchDB Installation###
* [Installing CouchDB on Ubuntu]
* [Installing CouchDB on OSX]

Setup
-----

1. Ensure that the ccollab command line client is configured:
```sh
ccollab login
```
2. Push design documents to CouchDB:
```sh
cd <heimdall_home>
python heimdall/setup/couchdbpush.py
```

###Data Loading###
Heimdall requires data from two sources: a git repository and a CodeCollaborator review system.

To load a git commit:
```sh
cd <heimdall_home>
python heimdall/dataload/gitdataloader.py <full_git_commit_sha1>
```

To load a CodeCollaborator review:
```sh
cd <heimdall_home>
python heimdall/dataload/ccollabdataloader.py <ccollab_review_id>
```

Development
-----------

Most map-reduce development will likely occur on CouchDB itself. To support this, Heimdall comes with a sync utility to pull design documents from CouchDB:
```sh
cd <heimdall_home>
python heimdall/setup/couchdbsync.py
git commit -a
```
Note that CouchDB sync and CouchDB push are meant to be used in concert.

[Couchdbkit Module]:http://couchdbkit.org/download.html
[Requests Module]:http://docs.python-requests.org/en/latest/user/install/
[xmltodict Module]:https://github.com/martinblech/xmltodict
[Installing CouchDB on Ubuntu]:https://wiki.apache.org/couchdb/Installing_on_Ubuntu
[Installing CouchDB on OSX]:https://wiki.apache.org/couchdb/Installing_on_OSX

