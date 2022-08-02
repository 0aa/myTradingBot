from multiprocessing import Pool
import time
from finta.finta import TA

def run_loop(p):
    x=99999
    print(x)
    return x**x


if __name__ == '__main__':
    rng = 50


    t = time.time()
    for i in range(rng):
        run_loop(i)
    print('time ran loop', time.time() - t)

    '''
    t = time.time()
    for x in rng:
        x ** x
    print('time ran loop#2', time.time() - t)
    '''

    t = time.time()
    pool = Pool()  # on 8 processors
    pool.imap_unordered(run_loop, range(rng))
    pool.close()
    pool.join()
    print('time ran pool', time.time() - t)


    # start 4 worker processes
    # with Pool(processes=4) as pool:




    '''
        # print "[0, 1, 4,..., 81]"
        print(pool.map(f, range(10)))

        # print same numbers in arbitrary order
        for i in pool.imap_unordered(f, range(10)):
            print(i)

        # evaluate "f(10)" asynchronously
        res = pool.apply_async(f, [10])
        print(res.get(timeout=1))             # prints "100"

        # make worker sleep for 10 secs
        res = pool.apply_async(sleep, [10])
        print(res.get(timeout=1))             # raises multiprocessing.TimeoutError

    # exiting the 'with'-block has stopped the pool
    '''