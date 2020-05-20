import base64
import yaml


class DocumentService:
    @staticmethod
    def json_to_bytes_encoded_yaml(json):
        document_yaml = yaml.dump(json, allow_unicode=True)
        encoded_yaml = base64.b64encode(bytes(document_yaml, 'utf-8'))
        return encoded_yaml

    @staticmethod
    def bytes_encoded_yaml_to_dict(encoded_yaml):
        decoded_yaml = base64.b64decode(encoded_yaml).decode('utf-8')
        dict_from_yaml = yaml.load(decoded_yaml, Loader=yaml.FullLoader)
        return dict_from_yaml
