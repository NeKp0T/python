import numpy as np
import numbers
import types


class AutoStrMixin:

    def __str__(self):
        name = self.__class__.__name__ + ': '
        attrs = [f'{k}={v}' for (k, v) in self.__dict__.items()]
        return name + ', '.join(attrs)

    def __repr__(self):
        return str(self)

    def save_to_file(self, file):
        print(self, file=file)


class MatrixDimensionMismatch(Exception):
    pass


class Matrix(np.lib.mixins.NDArrayOperatorsMixin, AutoStrMixin):

    def __init__(self, data):
        self.n = len(data)
        if self.n == 0:
            self.m = 0
        else:
            self.m = len(data[0])

        self.data = np.ndarray((self.n, self.m), dtype=type(data[0][0]))
        for i, row in enumerate(data):
            if len(row) != self.m:
                raise MatrixDimensionMismatch(
                    f"Row {i} of init data has length {len(row)}, but row 0 has length {self.m}")
            self.data[i] = np.array(row)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        # print(ufunc, method, inputs, kwargs)
        out = kwargs.get('out', ())
        for x in inputs + out:
            # Only support operations with instances of _HANDLED_TYPES.
            # Use ArrayLike instead of type(self) for isinstance to
            # allow subclasses that don't override __array_ufunc__ to
            # handle ArrayLike objects.
            if not isinstance(x, (np.ndarray, numbers.Number, type(self),)):
                return NotImplemented

        # Defer to the implementation of the ufunc on unwrapped values.
        inputs = tuple(x.data if isinstance(x, Matrix) else x
                       for x in inputs)
        if out:
            kwargs['out'] = tuple(
                x.data if isinstance(x, Matrix) else x
                for x in out)
        result = getattr(ufunc, method)(*inputs, **kwargs)

        if type(result) is tuple:
            # multiple return values
            return tuple(type(self)(x) for x in result)
        elif method == 'at':
            # no return value
            return None
        else:
            # one return value
            return type(self)(result)

    # def __repr__(self):
    #     return '%s(%r)' % (type(self).__name__, self.data)

    def T(self):
        return Matrix([[self.data[j][i] for j in range(self.m)] for i in range(self.n)])


def print_matrix(M, **kargs):
    for row in M.data:
        print(*row, **kargs)

if __name__ == "__main__":
    import os
    import numpy as np
    np.random.seed(0)

    A = Matrix(np.random.randint(0, 10, (10, 10)))
    B = Matrix(np.random.randint(0, 10, (10, 10)))
    # print(A)

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass
    try:
        os.mkdir("artifacts/medium")
    except OSError as _:
        pass

    with open("artifacts/medium/matrix+.txt", "w") as file:
        (A + B).save_to_file(file)
    with open("artifacts/medium/matrix*.txt", "w") as file:
        (A * B).save_to_file(file)
    with open("artifacts/medium/matrix@.txt", "w") as file:
        (A @ B).save_to_file(file)
