Backup Monkey
=============

.. image:: https://travis-ci.org/Answers4AWS/backup-monkey.png?branch=master
   :target: https://travis-ci.org/Answers4AWS/backup-monkey
   :alt: Build Status

A monkey that makes sure you have a backup of your EBS volumes in case something goes wrong. 

It is designed specifically for Amazon Web Services (AWS), and uses Python and Boto.

This script is designed to be run on a schedule, probably by CRON. 

Usage
-----

::

    usage: backup-monkey [-h] [--region REGION]
                         [--max-snapshots-per-volume SNAPSHOTS] [--snapshot-only]
                         [--remove-only] [--verbose] [--version]
                         [--tags TAGS [TAGS ...]] [--reverse-tags]
                         [--cross-account-number CROSS_ACCOUNT_NUMBER]
                         [--cross-account-role CROSS_ACCOUNT_ROLE]

    Loops through all EBS volumes, and snapshots them, then loops through all
    snapshots, and removes the oldest ones.

    optional arguments:
      -h, --help            show this help message and exit
      --region REGION       the region to loop through and snapshot (default is
                            current region of EC2 instance this is running on).
                            E.g. us-east-1
      --max-snapshots-per-volume SNAPSHOTS
                            the maximum number of snapshots to keep per EBS
                            volume. The oldest snapshots will be deleted. Default:
                            3
      --snapshot-only       Only snapshot EBS volumes, do not remove old snapshots
      --remove-only         Only remove old snapshots, do not create new snapshots
      --verbose, -v         enable verbose output (-vvv for more)
      --version             display version number and exit
      --tags TAGS [TAGS ...]
                            Only snapshot instances that match passed in tags.
                            E.g. --tag Name:foo will snapshot all instances with a
                            tag `Name` and value is `foo`
      --reverse-tags        Do a reverse match on the passed in tags. E.g. --tag
                            Name:foo --reverse-tags will snapshot all instances
                            that do not have a `Name` tag with the value `foo`
      --cross-account-number CROSS_ACCOUNT_NUMBER
                            Do a cross-account snapshot (this is the account
                            number to do snapshots on). NOTE: This requires that
                            you pass in the --cross-account-role parameter. E.g.
                            --cross-account-number 111111111111 --cross-account-
                            role Snapshot
      --cross-account-role CROSS_ACCOUNT_ROLE
                            The name of the role that backup-monkey will assume
                            when doing a cross-account snapshot. E.g. --cross-
                            account-role Snapshot

Examples
--------

Create snapshots of all EBS volumes in us-east-1:

::

    backup-monkey --region us-east-1

Delete snapshots of EBS volumes in us-west-1 where a volume has more than 5 snapshots:

::

    backup-monkey --region us-west-1 --max-snapshots-per-volume 5 --remove-only


Installation
------------

You can install Backup Monkey using the usual PyPI channels. Example:

::

    sudo pip install backup_monkey
    
You can find the package details here: https://pypi.python.org/pypi/backup_monkey

Alternatively, if you prefer to install from source:

::

    git clone git@github.com:Answers4AWS/backup-monkey.git
    cd backup-monkey
    python setup.py install


Configuration
-------------

This project uses `Boto <http://boto.readthedocs.org/en/latest/index.html>`__ to
call the AWS APIs. You can pass your AWS credentials to Boto can by using a
:code:`.boto` file, IAM Roles or environment variables. Full information can be
found here:

http://boto.readthedocs.org/en/latest/boto_config_tut.html


Warning
-------

Make no mistake. This script WILL delete snapshots. This script WILL create
snapshots, which can cost you money. There really are no warranties or
guarantees. For costs, refer to http://aws.amazon.com/ec2/pricing/


Source Code
-----------

The Python source code for Backup Monkey is available on GitHub:

https://github.com/Answers4AWS/backup-monkey


About Answers for AWS
---------------------

This code was written by `Peter
Sankauskas <https://twitter.com/pas256>`__, founder of `Answers for
AWS <http://answersforaws.com/>`__ - a company focused on helping businesses
learn how to use AWS, without doing it the hard way. If you are looking for help
with AWS, please `contact us <http://answersforaws.com/contact/>`__.


License
-------

Copyright 2013 Answers for AWS LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
law or agreed to in writing, software distributed under the License is
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.
      
