import time
import threading
import traceback
from collections import defaultdict
import sys
import linecache

line_stats = defaultdict(lambda: {'count': 0, 'time': 0.0})
current_line_start = None


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

def build_call_tree():
    tree = {}
    for stack in samples:
        current = tree
        for func in stack:
            current = current.setdefault(func, {'count':0, 'children':{}})
            current['count']+=1
    return tree

def print_tree(tree, indent=0, threshold=5):
    for func, data in sorted(tree.items(), key=lambda x:x[1]['count'], reverse=True):
        if data['count'] >= threshold:
            print("  " * indent + f"{func} ({data['count']})")   
            print_tree(data['children'], indent+1, threshold)

def flamegraph():
    print("\nFlamegraph (wider = more time):")
    hotspots = analyze_samples()
    max_count = max(hotspots.values()) if hotspots else 1
    for func, count in sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:10]:
        name = func.split(':')[1] if ':' in func else func
        bar = "█" * int(50 * count / max_count)
        print(f"{name[:30]:30} {bar} {count}")



def trace_lines(frame, event, arg):
    global current_line_start
    if event == 'line':
        if current_line_start:
            duration = time.perf_counter() - current_line_start
            key = (frame.f_code.co_filename, frame.f_lineno)
            line_stats[key]['count'] += 1
            line_stats[key]['time'] += duration
        current_line_start = time.perf_counter()
    return trace_lines

def line_profile(func):
    def wrapper(*args, **kwargs):
        sys.settrace(trace_lines)
        result = func(*args, **kwargs)
        sys.settrace(None)
        return result
    return wrapper
def show_line_stats(filename):
    print(f"\nLine-by-line profile for {filename}:")
    for (fname, lineno), data in sorted(line_stats.items()):
        if filename in fname:
            print(f"Line {lineno} :{data['count']} hits , {data['time']:.6f}s total")


@line_profile
def process_data():
    data = list(range(1000000))
    filtered = [x for x in data if x % 2 == 0 ]
    total = sum(filtered)
    return total



def show_line_stats_pretty(filename):
    print(f"\nLine-by-line profile:")
    for (fname, lineno), data in sorted(line_stats.items(), key=lambda x: x[1]['time'], reverse=True):
        if filename in fname:
            code = linecache.getline(fname, lineno).strip()
            print(f"Line {lineno:3d} | {data['time']:8.4f}s | {code[:60]}")
result = process_data()
print(f"\nTotal entries collected: {len(line_stats)}")
print(f"First few entries: {list(line_stats.items())[:3]}")
show_line_stats_pretty('profiler.py')
# Replace the test code at bottom
print("=== DECORATOR PROFILING ===")
for _ in range(5):
    slow_function()
    fast_function()
report()
show_calls()

print("\n=== SAMPLING PROFILER ===")
samples.clear()
start_sampling(0.001)
for _ in range(50):
    slow_function()
stop_sampling()
flamegraph()