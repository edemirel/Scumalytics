import multiprocessing
import time

range = 256*256


def f(name):
    print 'hello', name
    return None


def main1():
    pool = multiprocessing.Pool()  # use all available cores, otherwise specify the number you want as an argument
    for i in xrange(0, range):
        pool.apply(f, args=(i,))
    pool.close()
    pool.join()


def main2():
    for i in xrange(0, range):
        print f(i)

if __name__ == '__main__':
    start = time.time()
    main1()
    end = time.time()
    print "{0:.2f}".format((end-start)/60)
