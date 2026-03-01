from typing import Callable
from functools import wraps
from contextlib import contextmanager

# синхронные
def parametrize_wrapper(limit: int):
    def wrapper(func: Callable):
        @wraps(func)  # возвращаем __doc__ и __name__ декорируемой функции
        def inner(*args, **kwargs):
            nonlocal limit
            print(f'{limit=}')
            if limit == 0:
                return print('The call limit reached')
            else:
                res = func(*args, **kwargs)
                limit -= 1
                return res
        return inner
    return wrapper


@parametrize_wrapper(2)
def func(a: int, b: int):
    """Documentation of func."""
    return a + b

# print(func.__doc__)
print(func(1, 2))
print(func(2, 2))
print(func(3, 2))
print(func(4, 2))



# Асинхронные декораторы
from typing import Coroutine
import asyncio

def deco(coroutine: Coroutine):
    async def wrapper(*args, **kwargs):
        res = await coroutine(*args, **kwargs)
        return res
    return wrapper

@deco
async def async_func(a: int, b: int):
    """Documentation of async func."""
    await asyncio.sleep(0.5)
    print('a')
    return a + b

res = asyncio.run(async_func(2, 3))
print(res)


async def main():
    res2 = await async_func(1, 2)
    print(res2)

asyncio.run(main())