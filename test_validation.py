from pydantic import validate_call
from typing import Annotated
# from pydantic.types import Gt, Ge, Le
# from annotated_types import Gt, Ge, Le
from pydantic.types import Gt, Ge, Le


def check_exeption1(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except ValueError:
            print('Ошибка входных данных')
            return None
    return wrapper


@check_exeption1
@validate_call
def calculate_discount(
    price: Annotated[float, Gt(0)],
    discount: Annotated[float, Ge(0), Le(100)]
) -> float:
    return price * (1 - discount / 100)


while True:
    price = float(input('price='))
    disc = float(input('%='))
    result = calculate_discount(price, disc)
    print(type(result))
    print(result)
