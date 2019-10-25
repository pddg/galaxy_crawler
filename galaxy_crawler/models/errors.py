import json


class InvalidParameter(Exception):

    def __init__(self, param, expected):
        self.param = param
        self.expected = expected

    def __str__(self):
        return f"Param '{self.param}' is invalid. Expected: {self.expected}"


class InsufficientParameter(Exception):

    def __init__(self, param_name: str, env_var_prefix: str = None):
        self.param_name = param_name
        self.env_var_prefix = env_var_prefix if env_var_prefix else ""

    def __str__(self):
        env_var = f"{self.env_var_prefix.upper()}_{self.param_name.upper()}"
        return f"'{env_var}' is not specified."


class JSONParseFailed(Exception):

    def __init__(self, model: 'str', json_obj: 'dict'):
        self.model = model
        self.json_obj = json_obj

    def __str__(self) -> str:
        return f"Could not parse json for model '{self.model}'." \
            f"json: {json.dumps(self.json_obj, ensure_ascii=False)}"
