import time

start = time.perf_counter()

end = time.perf_counter()
print(f"Time taken: {end - start: . 6f} seconds")


stats = {}

stats = {}

def profile(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        name = func.__name__
        stats[name] = stats.get(name, {'time': 0, 'calls': 0})
        stats[name]['time'] += duration
        stats[name]['calls'] += 1
        return result
    return wrapper