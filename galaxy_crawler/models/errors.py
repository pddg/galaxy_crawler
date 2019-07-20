import json


class JSONParseFailed(Exception):

    def __init__(self, model: 'str', json_obj: 'dict'):
        self.model = model
        self.json_obj = json_obj

    def __str__(self) -> str:
        return f"Could not parse json for model '{self.model}'." \
            f"json: {json.dumps(self.json_obj, ensure_ascii=False)}"


class DateParseFailed(Exception):

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
