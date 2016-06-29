def calc_sum(start, end):
    sum = 0
    for i in range(start, end + 1):
        sum += 1 / i
    return sum


if __name__ == '__main__':
    print(calc_sum(2, 3))