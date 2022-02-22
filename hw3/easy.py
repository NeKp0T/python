
class MatrixDimensionMismatch(Exception):
    pass


class Matrix:

    def __init__(self, data):
        self.n = len(data)
        if self.n == 0:
            self.m = 0
        else:
            self.m = len(data[0])

        self.data = []
        for i, row in enumerate(data):
            if len(row) != self.m:
                raise MatrixDimensionMismatch(
                    f"Row {i} of init data has length {len(row)}, but row 0 has length {self.m}")
            # copy data to ensure it's stored in a list
            self.data.append([x for x in row])

    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()

        if self.m != other.m:
            raise MatrixDimensionMismatch(
                "Matrix dimension mismatch during (+): {self.n}x{self.m} + {other.n}x{other.m}")

        return Matrix(
            [
                [x1 + x2 for x1, x2 in zip(row1, row2)]
                for row1, row2 in zip(self.data, other.data)
            ]
        )

    def __mul__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()

        if self.n != other.n or self.m != other.m:
            raise MatrixDimensionMismatch(
                "Matrix dimension mismatch during (*): {self.n}x{self.m} * {other.n}x{other.m}")

        return Matrix(
            [
                [x1 * x2 for x1, x2 in zip(row1, row2)]
                for row1, row2 in zip(self.data, other.data)
            ]
        )

    def T(self):
        return Matrix([[self.data[j][i] for j in range(self.m)] for i in range(self.n)])

    def __matmul__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()

        if self.m != other.n:
            raise MatrixDimensionMismatch(
                "Matrix dimension mismatch during (@): {self.n}x{self.m} @ {other.n}x{other.m}")

        return Matrix(
            [
                [sum(map(lambda xy: xy[0] * xy[1], zip(row1, col2)))
                 for col2 in other.T().data]
                for row1 in self.data
            ]
        )


def print_matrix(M, **kargs):
    for row in M.data:
        print(*row, **kargs)

if __name__ == "__main__":
    import os
    import numpy as np
    np.random.seed(0)

    A = Matrix(np.random.randint(0, 10, (10, 10)))
    B = Matrix(np.random.randint(0, 10, (10, 10)))

    try:
        os.mkdir("artifacts")
    except OSError as _:
        pass
    try:
        os.mkdir("artifacts/easy")
    except OSError as _:
        pass

    with open("artifacts/easy/matrix+.txt", "w") as file:
        print_matrix(A + B, file=file)
    with open("artifacts/easy/matrix*.txt", "w") as file:
        print_matrix(A * B, file=file)
    with open("artifacts/easy/matrix@.txt", "w") as file:
        print_matrix(A @ B, file=file)
