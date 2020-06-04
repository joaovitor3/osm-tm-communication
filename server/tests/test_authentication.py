from server.tests.base_test_config import BaseTestCase
from flask_restful import Api
from server.api.authentication.resources import AuthenticationApi


class TestDocument(BaseTestCase):
    def test_document(self):
        a = Api()
        response = self.client.get(a.url_for(AuthenticationApi))
        self.assertEqual(response.status_code, 200)
