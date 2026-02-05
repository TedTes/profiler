import time

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

def report():
    for name, data in sorted(stats.items(), key=lambda x: x[1]['time'], reverse=True):
        avg = data['time'] / data['calls']
        print(f"{name}: {data['calls']} calls, {data['time']:.4f}s total, {avg:.4f}s avg")

@profile
def slow_function():
    time.sleep(0.1)
    
@profile
def fast_function():
    sum(range(1000))

for _ in range(5):
    slow_function()
    fast_function()
    
report()