import time
import threading
import traceback


import sys

call_stack = []
sampling_active = False
samples = []

stats = {}
def get_caller():
    frame = sys._getframe(2)
    return frame.f_code.co_name if frame else None


def profile(func):
    def wrapper(*args, **kwargs):
        caller = get_caller()
        call_stack.append((caller, func.__name__))
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

def show_calls():
    print("\nCall Graph:")
    for caller, callee in call_stack:
        indent = "  " if caller else ""
        print(f"{indent}{caller or 'main'} -> {callee}")
@profile
def slow_function():
    time.sleep(0.1)
    
@profile
def fast_function():
    sum(range(1000))

def sample_stack():
    for frame in sys._current_frames().values():
        stack = traceback.extract_stack(frame);
        samples.append([f"{s.filename}:{s.name}:{s.lineno}" for s in stack])

def start_sampling(interval=0.01):
    global sampling_active
    sampling_active = True
    threading.Timer(interval, lambda: sample_loop(interval)).start()

def sample_loop(interval):
    if sampling_active:
        sample_stack()
        threading.Timer(interval, lambda: sample_loop(interval)).start()
def stop_sampling():
    global sampling_active
    sampling_active = False     

def analyze_samples():
    print(f"\nCollected {len(samples)} samples")
    # Count function appearances
    func_count = {}
    for stack in samples:
        for func in stack:
            func_count[func] = func_count.get(func, 0) + 1
    return func_count

start_sampling()
for _ in range(10):
    slow_function()
stop_sampling()

hotspots = analyze_samples()
for func, count in sorted(hotspots.items(), key= lambda x: x[1], reverse=True)[:5]:
    print(f"{func}: {count} times")

for _ in range(5):
    slow_function()
    fast_function()

show_calls()
report()
