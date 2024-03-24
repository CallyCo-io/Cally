from dynaconf import Validator  # type: ignore


def is_lowercase(value: str) -> bool:
    return value.islower()


OPERATIONS_MESSAGE = {
    'operations': '{name} must {operation} {op_value}, but is: {value}'
}

BASE_CALLY_CONFIG = [
    Validator(
        'NAME',
        is_type_of=str,
        condition=is_lowercase,
        messages={'condition': 'Name must be lowercase'},
    ),
    Validator(
        'ENVIRONMENT',
        is_type_of=str,
        messages=OPERATIONS_MESSAGE,
    ),
    Validator(
        'STACK_TYPE',
        is_type_of=str,
        messages=OPERATIONS_MESSAGE,
    ),
    Validator('PROVIDERS', is_type_of=dict, messages=OPERATIONS_MESSAGE),
    Validator(
        'STACK_VARS',
        is_type_of=dict,
        messages=OPERATIONS_MESSAGE,
    ),
    Validator("BACKEND.type", is_type_of=str, messages=OPERATIONS_MESSAGE),
    Validator("BACKEND.path", is_type_of=str, messages=OPERATIONS_MESSAGE),
    Validator("BACKEND.key", is_type_of=str, messages=OPERATIONS_MESSAGE),
]
