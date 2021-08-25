import os
from unittest import TestCase

from tasks.Tasks import Tasks


class TestTasks(TestCase):
    def test_add_task(self):
        tasks = Tasks('tenant_one')
        with open('../test_files/test.pdf', 'rb') as file:
            tasks.add('test.pdf', file.read())

        self.assertTrue(os.path.exists('../docker_volume/to_segment/tenant_one/test.pdf'))
        os.remove('../docker_volume/to_segment/tenant_one/test.pdf')
        os.rmdir('../docker_volume/to_segment/tenant_one')
