import cython


@cython.cdivision(True)
@cython.boundscheck(False)
@cython.nonecheck(False)
@cython.wraparound(False)
cpdef  float calc_sum_cython(int start, int end):
    cdef float sum = 0
    cdef int i = 0
    for i in range(start, end + 1):
        sum += (1. / i)
    return sum
