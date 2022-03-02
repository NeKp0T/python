from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import concurrent.futures
import math
import multiprocessing
import os
import time

from easy import time_elapsed

def log_to_file(filename, text):
    if filename is not None:
        with open(filename, "a") as fout:
            print(text, file=fout)

def integrate_worker(f, a, step, i_from, i_to, job_num, logfile):
    log_to_file(logfile, f"[{time.time()}] {job_num} starts")

    acc = 0
    for i in range(i_from, i_to):
        acc += f(a + i * step) * step

    log_to_file(logfile, f"[{time.time()}] {job_num} ends")

    return acc


def integrate(f, a, b, executor: concurrent.futures.Executor, n_jobs=1, n_iter=1000, logfile=None):
    step = (b - a) / n_iter

    futures: list[concurrent.futures.Future] = []
    for job_i in range(n_jobs):
        i_from = n_iter * job_i // n_jobs
        i_to = n_iter * (job_i + 1) // n_jobs
        future = executor.submit(
            integrate_worker, f, a, step, i_from, i_to, job_i, logfile)
        futures.append(future)

    acc = 0
    for future in futures:
        acc += future.result()

    return acc


if __name__ == "__main__":
    n_iter = 10**7
    logfile = "artifacts/medium_log.txt"
    results_file = "artifacts/medium_results.txt"

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass

    with open(logfile, "w") as output:
        print("-------START-------", file=output)
    with open(results_file, "w") as output:
        print("-------START-------", file=output)

    def run_on_pool(executor):
        executor_class_name = executor.__class__.__name__.split(".")[-1]
        log_to_file(logfile, f"{executor_class_name}, {n_jobs} jobs")
        def work():
            return integrate(math.cos, 0, math.pi / 2, executor,
                             n_jobs=n_jobs, n_iter=n_iter, logfile=logfile)
        res, time = time_elapsed(work)
        log_to_file(logfile, f"Result: {res}")
        log_to_file(logfile, f"TIme:   {time}")

        log_to_file(results_file, f"{executor_class_name}, {n_jobs} jobs:\nTime: {time}")

    for n_jobs in range(1, multiprocessing.cpu_count() * 2):
        with ThreadPoolExecutor(n_jobs) as executor:
            run_on_pool(executor)
        with ProcessPoolExecutor(n_jobs) as executor:
            run_on_pool(executor)
