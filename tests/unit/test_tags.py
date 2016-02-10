from unittest import TestCase
import mock
from backup_monkey.core import BackupMonkey

class MockVolume(object):
    def __init__(self, id, tags={}):
        self.id = id
        self.tags = tags

class MockSnapshot(object):
    def __init__(self, id, description, start_time):
        self.id = id
        self.volume_id = 'vol-fb07ec3a'
        self.description = description
        self.start_time = start_time
        self.status = 'completed'
    def delete(self):
        self.status = 'deleted'

tag = ['name:foo']
tag_or = ["name:['bar','baz']"]
tag_multiple = ['name:foo', 'customer:bar']

def params_to_dict(params):
    ret = []
    for p in params:
        v = p.split(':')
        try:
            v[1] = eval(v[1])
        except Exception:
            pass
        if isinstance(v[1], list):
            for x in v[1]:
                ret = ret + [v[0], x]
        else:
            ret = ret + v 
    return dict(zip(ret[0::2], ret[1::2]))

a = MockVolume('vol-fb07ec3a')
b = MockVolume('vol-089322fc') 
# matches ['name:foo']
match_tag = MockVolume('vol-d815a12c', params_to_dict(tag))
# matches ['name:bar']
match_tag_or_1 = MockVolume('vol-c2922336', dict([(tag_or[0].split(':')[0], eval(tag_or[0].split(':')[1])[0])]))
# matches ['name:baz']
match_tag_or_2 = MockVolume('vol-99bf3b6d', dict([(tag_or[0].split(':')[0], eval(tag_or[0].split(':')[1])[1])]))
# matches ['name:foo', 'customer:bar']
match_tag_multiple = MockVolume('vol-d59b7114', params_to_dict(tag_multiple))

volumes = [a, match_tag, match_tag_or_1, b, match_tag_or_2, match_tag_multiple]

def create_snapshots():
    snap_manual = MockSnapshot('snap-1a2b3c4d', 'no backup monkey', '2016-01-01T10:00:00.000Z')
    snap_daily = MockSnapshot('snap-2a2b3c4d', 'BACKUP_MONKEY daily vol-fb07ec3a', '2016-01-01T11:00:00.000Z')
    snap_weekly = MockSnapshot('snap-3a2b3c4d', 'BACKUP_MONKEY weekly vol-fb07ec3a', '2016-01-01T12:00:00.000Z')
    snap_weekly2 = MockSnapshot('snap-4a2b3c4d', 'BACKUP_MONKEY weekly vol-fb07ec3a', '2016-01-01T13:00:00.000Z')
    return [snap_manual, snap_daily, snap_weekly, snap_weekly2]


class MockEC2Connection(object):
    def __init__(self):
        self.snapshots = create_snapshots()

    def get_all_volumes(self, filters=[]):
        if filters:
            if isinstance(filters['tag:name'], list):
                return [v for v in volumes if 'name' in v.tags and v.tags['name'] in filters['tag:name']]
            else:
                return [v for v in volumes if 'name' in v.tags and v.tags['name'] == filters['tag:name']]
        return volumes

    def get_all_snapshots(self, owner='self'):
        return self.snapshots

def mock_get_connection():
    return MockEC2Connection() 

class TagsTest(TestCase):

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def setUp(self, mock):
        self.backup_monkey = BackupMonkey('us-west-2', 3, [], None, None, None, None)

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_instance(self, mock):
        assert isinstance(self.backup_monkey.get_connection(), MockEC2Connection) == True
        assert self.backup_monkey.get_volumes_to_snapshot() == volumes

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_no_tag(self, mock):
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 6
        assert ret == volumes 

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag(self, mock):
        self.backup_monkey._tags = tag
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 2
        assert ret == [match_tag, match_tag_multiple]

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag_or(self, mock):
        self.backup_monkey._tags = tag_or
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 2 
        assert ret == [match_tag_or_1, match_tag_or_2]

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag_multiple(self, mock):
        self.backup_monkey._tags = tag_multiple
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 2
        assert ret == [match_tag, match_tag_multiple]

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag_reverse_tags(self, mock):
        self.backup_monkey._tags = tag
        self.backup_monkey._reverse_tags = True
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 4
        assert ret == [a, match_tag_or_1, b, match_tag_or_2]

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag_or_reverse_tags(self, mock):
        self.backup_monkey._tags = tag_or 
        self.backup_monkey._reverse_tags = True
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 4 
        assert ret == [a, match_tag, b, match_tag_multiple]

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_tag_multiple_reverse_tags(self, mock):
        self.backup_monkey._tags = tag_multiple
        self.backup_monkey._reverse_tags = True
        ret = self.backup_monkey.get_volumes_to_snapshot()
        assert len(ret) == 4
        assert ret == [a, match_tag_or_1, b, match_tag_or_2]

class LabelTest(TestCase):

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def setUp(self, mock):
        self.bm = BackupMonkey('us-west-2', 1, [], None, None, None, None)
        self.bm_with_label_daily = BackupMonkey('us-west-2', 1, [], None, 'daily', None, None)
        self.bm_with_label_weekly = BackupMonkey('us-west-2', 1, [], None, 'weekly', None, None)

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_without_label(self, mock):
        snaps = self.bm._conn.get_all_snapshots()
        init_snapshot = filter(lambda x: x.status == 'completed', snaps)
        self.bm.remove_old_snapshots()
        snaps = self.bm._conn.get_all_snapshots()
        end_snapshot = filter(lambda x: x.status == 'completed', snaps)
        assert len(init_snapshot) == 4
        assert len(end_snapshot) == 2

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_with_label_daily(self, mock):
        snaps = self.bm_with_label_daily._conn.get_all_snapshots()
        init_snapshot = filter(lambda x: x.status == 'completed', snaps)
        self.bm_with_label_daily.remove_old_snapshots()
        snaps = self.bm_with_label_daily._conn.get_all_snapshots()
        end_snapshot = filter(lambda x: x.status == 'completed', snaps)
        assert len(init_snapshot) == 4
        assert len(end_snapshot) == 4

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def test_with_label_weekly(self, mock):
        snaps = self.bm_with_label_weekly._conn.get_all_snapshots()
        init_snapshot = filter(lambda x: x.status == 'completed', snaps)
        self.bm_with_label_weekly.remove_old_snapshots()
        snaps = self.bm_with_label_weekly._conn.get_all_snapshots()
        end_snapshot = filter(lambda x: x.status == 'completed', snaps)
        assert len(init_snapshot) == 4
        assert len(end_snapshot) == 3
