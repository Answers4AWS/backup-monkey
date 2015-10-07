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

from unittest import TestCase

from backup_monkey.exceptions import * 

class ExceptionTests(TestCase):
    def test_new_exception(self):
        e = BackupMonkeyException()
        self.assertTrue(isinstance(e, BackupMonkeyException))
        #self.assertIsInstance(e, BackupMonkeyException)

    def raise_BackupMonkeyException(self):
        raise BackupMonkeyException('msg')
    
    def test_raise_BackupMonkeyException(self):
        self.assertRaises(BackupMonkeyException, self.raise_BackupMonkeyException)
