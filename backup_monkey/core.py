# Copyright 2013 Answers for AWS LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

import boto
from boto import ec2

from backup_monkey.exceptions import BackupMonkeyException

__all__ = ('BackupMonkey', 'Logging')
log = logging.getLogger(__name__)


class BackupMonkey(object):
    def __init__(self, region, max_snapshots_per_volume):
        self._region = region
        self._prefix = 'BACKUP_MONKEY'
        self._snapshots_per_volume = max_snapshots_per_volume
        
        log.info("Connecting to region %s", self._region)
        try:
            self._conn = ec2.connect_to_region(self._region)
        except boto.exception.NoAuthHandlerFound:
            log.error('Could not connect to region %s' % self._ami_region)
            log.critical('No AWS credentials found. To configure Boto, please read: http://boto.readthedocs.org/en/latest/boto_config_tut.html')
            raise BackupMonkeyException('No AWS credentials found')            

    
    def snapshot_volumes(self):
        ''' Loops through all EBS volumes and creates snapshots of them '''
        
        log.info('Getting list of EBS volumes')
        volumes = self._conn.get_all_volumes()
        log.info('Found %d volumes', len(volumes))
        for volume in volumes:            
            description_parts = [self._prefix]
            description_parts.append(volume.id)
            if volume.attach_data.instance_id:
                description_parts.append(volume.attach_data.instance_id)
            if volume.attach_data.device:
                description_parts.append(volume.attach_data.device)
            description = ' '.join(description_parts)
            log.info('Creating snapshot of %s: %s', volume.id, description)
            volume.create_snapshot(description)
        return True


    def remove_old_snapshots(self):
        ''' Loop through this account's snapshots, and remove the oldest ones
        where there are more snapshots per volume than required '''
        
        log.info('Configured to keep %d snapshots per volume', self._snapshots_per_volume)
        log.info('Getting list of EBS snapshots')
        snapshots = self._conn.get_all_snapshots(owner='self')
        log.info('Found %d snapshots', len(snapshots))
        vol_snap_map = {}
        for snapshot in snapshots:
            if not snapshot.description.startswith(self._prefix):
                log.debug('Skipping %s as prefix does not match', snapshot.id)
                continue
            if not snapshot.status == 'completed':
                log.debug('Skipping %s as it is not a complete snapshot', snapshot.id)
                continue
            
            log.debug('Found %s: %s', snapshot.id, snapshot.description)
            vol_snap_map.setdefault(snapshot.volume_id, []).append(snapshot)
            
        for volume_id, most_recent_snapshots in vol_snap_map.iteritems():
            most_recent_snapshots.sort(key=lambda s: s.start_time, reverse=True)
            num_snapshots = len(most_recent_snapshots)
            log.info('Found %d snapshots for %s', num_snapshots, volume_id)

            for i in range(self._snapshots_per_volume, num_snapshots):
                snapshot = most_recent_snapshots[i]
                log.info(' Deleting %s: %s', snapshot.id, snapshot.description)
                snapshot.delete()
        return True



class Logging(object):
    # Logging formats
    _log_simple_format = '%(asctime)s [%(levelname)s] %(message)s'
    _log_detailed_format = '%(asctime)s [%(levelname)s] [%(name)s(%(lineno)s):%(funcName)s] %(message)s'
    
    def configure(self, verbosity = None):
        ''' Configure the logging format and verbosity '''
        
        # Configure our logging output
        if verbosity >= 2:
            logging.basicConfig(level=logging.DEBUG, format=self._log_detailed_format, datefmt='%F %T')
        elif verbosity >= 1:
            logging.basicConfig(level=logging.INFO, format=self._log_detailed_format, datefmt='%F %T')
        else:
            logging.basicConfig(level=logging.INFO, format=self._log_simple_format, datefmt='%F %T')
    
        # Configure Boto's logging output
        if verbosity >= 4:
            logging.getLogger('boto').setLevel(logging.DEBUG)
        elif verbosity >= 3:
            logging.getLogger('boto').setLevel(logging.INFO)
        else:
            logging.getLogger('boto').setLevel(logging.CRITICAL)    
    
