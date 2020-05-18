import base64
import yaml


class DocumentService:
    def __init__(self, json):
        self.json = json

    def json_to_bytes_encoded_yaml(self):
        document_yaml = yaml.dump(self.json, allow_unicode=True)
        encoded_yaml = base64.b64encode(bytes(document_yaml, 'utf-8'))
        return encoded_yaml
