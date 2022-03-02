import os
from threading import Thread
import multiprocessing as mp
import time

def fib(n):
    if n <= 2:
        return 1
    return fib(n-1) + fib(n-2)


def time_elapsed(func, *args, **kwargs):
    start = time.time()
    res = func(*args, **kwargs)
    end = time.time()
    return res, end - start


def run_sync(func, *args, runs=1):
    for _ in range(runs):
        func(*args)


def run_threading(func, *args, runs=1):
    threads = []
    for _ in range(runs):
        t = Thread(target=func, args=args)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


def run_multiprocess(func, *args, runs=1):
    processes = []
    for _ in range(runs):
        p = mp.Process(target=func, args=args)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    func = fib
    runs = 10
    args = (33,)

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass

    with open("artifacts/easy.txt", "w") as output:
        print("CPUCOUNT:", mp.cpu_count(), file=output)
        _, sync_time = time_elapsed(run_sync, func, *args, runs=runs)
        print("SYNCR:", sync_time, file=output)
        _, threading_time = time_elapsed(run_threading, func, *args, runs=runs)
        print("THRED:", threading_time, file=output)
        _, mp_time = time_elapsed(run_multiprocess, func, *args, runs=runs)
        print("MULTP:", mp_time, file=output)
