from unittest import TestCase
import mock
from backup_monkey.core import BackupMonkey 

class MockVolume(object):
    def __init__(self, id, tags={}):
        self.id = id
        self.tags = tags

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

class MockEC2Connection(object):
    def get_all_volumes(self, filters=[]):
        if filters:
            if isinstance(filters['tag:name'], list):
                return [v for v in volumes if 'name' in v.tags and v.tags['name'] in filters['tag:name']]
            else:
                return [v for v in volumes if 'name' in v.tags and v.tags['name'] == filters['tag:name']]
        return volumes

def mock_get_connection():
    return MockEC2Connection() 

class TagsTest(TestCase):

    @mock.patch('backup_monkey.core.BackupMonkey.get_connection', side_effect=mock_get_connection)
    def setUp(self, mock):
        self.backup_monkey = BackupMonkey('us-west-2', 3, [], None, None, None)

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
