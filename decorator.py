import logging
import time
import signal
from functools import wraps

import tracemalloc
import pendulum

logging.basicConfig(
    filename="function.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def reverse_arr_decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result.reverse()
        return result

    return wrapper

# 1. Create a Decorator to Log Function Arguments and Return Value
def register_args_and_return_value_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Calling {func.__name__} with args = {args}, \
                     kwargs = {kwargs}")
        result = func(*args, **kwargs)
        logging.info(f"{func.__name__} returned {result}\n")
        return result

    return wrapper

# 2. Create a Decorator to Measure Function Execution Time
def time_execution_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic_ns()
        result = func(*args, **kwargs)
        time_execution = time.monotonic_ns() - start
        logging.info(f"{func.__name__} execution during \
                     {time_execution / 1_000_000} ms")
        return result

    return wrapper

# 3. Create a decorator to convert function return value type
def convert_return_type_decorator(type_to):
    if type_to is None:
        raise ValueError(
            'Not defined argument "type_to" for \
             convert_return_type_decorator(func, type_to)'
        )

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                converted_result = type_to(result)
            except (TypeError, ValueError) as error:
                raise TypeError(
                    f"Impossible type conversion {type(result)} to {type_to}"
                ) from error
            return converted_result

        return wrapper

    return decorator

# 4. Implement a Decorator to Cache Function Results
def cache_function_decorator(func):
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            return cache[key]
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    return wrapper

# 5. Implement a Decorator to Validate Function Arguments
def validate_arg_decorator(condition):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if condition(*args, **kwargs):
                return func(*args, **kwargs)
            else:
                raise ValueError("Passed invalid arguments")

        return wrapper

    return decorator

# 6. Implement a Decorator to Retry a Function on Failure
def retry_on_failure_decorator(max_returns=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            curr_returns = 0
            while curr_returns < max_returns:
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    curr_returns += 1
                    if curr_returns == max_returns:
                        raise
                    time.sleep(delay)

        return wrapper

    return decorator

def handler(signum, frame):
    raise TimeoutError("Time limit out!")

# 7. Implement a Decorator to Enforce Rate Limits on a Function
def enforce_rate_limit_decorator(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            signal.alarm(seconds)
            signal.signal(signal.SIGALRM, handler)
            try:
                result = func(*args, **kwargs)
            except:
                raise TimeoutError("Time limit out!")
            finally:
                signal.alarm(0)
            return result

        return wrapper

    return decorator

# 8. Implement a Decorator to Add Logging Functionality
def logging_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        decorated_func = register_args_and_return_value_decorator(
            time_execution_decorator(func)
        )
        return decorated_func(*args, **kwargs)

    return wrapper

# 9. Implement a decorator to handle exceptions with a default value
def handle_exceptions_default_value_decorator(default_value):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logging.exception(f"Except in func {func.__name__}: {e}\n")
                return default_value
            else:
                return result

        return wrapper

    return decorator

# 10. Implement a decorator to enforce type checking on arguments
def enforce_types_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        annotations = func.__annotations__
        arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
        for i, value in enumerate(args):
            if i >= len(arg_names):
                break
            name = arg_names[i]
            expected_type = annotations.get(name)
            if expected_type and not isinstance(value, expected_type):
                raise TypeError(
                    f"Аргумент '{name}' должен быть типа \
                      {expected_type.__name__}, "
                    f"но получил {type(value).__name__}"
                )

        for name, value in kwargs.items():
            expected_type = annotations.get(name)
            if expected_type and not isinstance(value, expected_type):
                raise TypeError(
                    f"Аргумент '{name}' должен быть типа \
                      {expected_type.__name__}, "
                    f"но получил {type(value).__name__}"
                )

        return func(*args, **kwargs)

    return wrapper

# 11. Implement a Decorator to Measure Memory Usage of a Function
def memory_usage_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        print(tracemalloc.get_traced_memory())
        tracemalloc.stop()
        return result

    return wrapper

# 12. Implement a Decorator for Caching with Expiration Time
def cache_expiration_date_decorator(**expiration_date):
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            index = str((args, kwargs))
            now = pendulum.now()
            if index in cache:
                if cache[index][1] > now:
                    return cache[index][0]
                result = func(*args, **kwargs)
                cache[index][0] = result
                cache[index][1] = now.add(**expiration_date)
            else:
                result = func(*args, **kwargs)
                cache[index] = [result, now.add(**expiration_date)]
            return result

        return wrapper

    return decorator

@cache_expiration_date_decorator(seconds=1)
def transform(list1, list2):
    result = []
    for i in list1:
        for j in list2:
            result.append(f"{i} + {j}")
    return result


print(transform([1, 2, 3], [4, 5, 6]))
print(transform([1, 2, 3], [4, 5, 6]))