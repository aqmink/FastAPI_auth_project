import json
from typing import Any
from inspect import Parameter, signature
from functools import wraps

from fastapi import Response


def _with_new_signature(**new_parameters):
    def get_signature(func):
        sig = signature(func)
        parameters = list(sig.parameters.values())
        parameters.pop()
        for name, value in new_parameters.items():
            if name not in parameters:
                parameters.append(
                    Parameter(
                        name=name,
                        kind=Parameter.POSITIONAL_OR_KEYWORD,
                        default=value
                    )
                )
        new_sig = sig.replace(parameters=parameters)

        @wraps(func)
        def wrapper(*args, **kwargs):
            for name, value in new_parameters.items():
                if name not in kwargs and len(args) <= len(parameters) - len(new_parameters):
                    kwargs[name] = value
            return func(*args, **kwargs)
        
        wrapper.__signature__ = new_sig
        return wrapper
    
    return get_signature


def get_response_content(response: Response):
    if not response.body:
        return {}
    return json.loads(response.body)


def set_response_body(response: Response, data: dict[str, Any]):
    response.body = json.dumps(data).encode("utf-8")
    response.headers["Content-Length"] = str(len(response.body))
    return response
