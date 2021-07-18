#! /usr/bin/env python

import time

# multithread
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

# multiprocess
# from concurrent.futures import ProcessPoolExecutor
# from multiprocessing import Lock

from tqdm import tqdm


def do_something(arg1, arg2, executor_id, rank):
    result1, result2 = arg1/10, arg2/10

    return result1, result2, executor_id, rank


def parallel_executor():
    # prepare data
    num = 100000
    data = []
    for i in tqdm(range(num), desc='prepare data'):
        data.append((i*10, i*2))

    # parallel processing
    lock = Lock()

    num_workers = 2
    pool = ThreadPoolExecutor(max_workers=num_workers)
    # pool = ProcessPoolExecutor(max_workers=num_workers)

    results = []
    # if want to write to file
    # results_file = open('result.txt', 'w', encoding='utf-8')
    pbar = tqdm(total=len(data), desc='process data')

    def do_something_done(future):
        if future.result():
            result1, result2, executor_id, rank = future.result()
            lock.acquire()
            results.append((result1, result2, executor_id, rank))
            # results_file.write(f'{result1}\t{result2}\t{executor_id}\n')
            lock.release()
            pbar.update()

    start = time.time()

    for rank, item in enumerate(data):
        arg1, arg2 = item
        future = pool.submit(do_something, arg1, arg2, rank%num_workers, rank)
        future.add_done_callback(do_something_done)

    pool.shutdown()
    pbar.close()

    print(f'time: {time.time() - start}')

    # make sure result is ordered
    assert len(results) == len(data)
    results = sorted(results, key=lambda x: x[-1])
    # results_file.close()

    # process results
    for res in results[:10]:
        print(res)


if __name__ == '__main__':
    parallel_executor()
