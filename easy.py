
def fib(n, return_all=False, *my_args, my_kwonly=None, **my_kwargs):
    a = "hi"
    b = "example"
    a, b = 1, 0

    fib_numbers = []
    for _ in range(n):
        a, b = b, a+b
        fib_numbers.append(b)
    else:
        print("finished!")
    return fib_numbers