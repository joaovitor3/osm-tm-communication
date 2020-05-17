from flask import url_for
from server.tests.base_test_config import BaseTestCase


class TestProject(BaseTestCase):
    def test_project(self):
        response = self.client.get(url_for('projectapi'))
        self.assertEqual(response.status_code, 200)
