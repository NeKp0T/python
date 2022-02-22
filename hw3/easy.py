import copy


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

    cached_matmul = {}

    def __matmul__(self, other):
        if not isinstance(other, Matrix):
            raise NotImplementedError()

        if hash((self, other)) in Matrix.cached_matmul.keys():
            print('cached!')
            return Matrix.cached_matmul[hash((self, other))]

        if self.m != other.n:
            raise MatrixDimensionMismatch(
                "Matrix dimension mismatch during (@): {self.n}x{self.m} @ {other.n}x{other.m}")

        res = Matrix(
            [
                [sum(map(lambda xy: xy[0] * xy[1], zip(row1, col2)))
                 for col2 in other.T().data]
                for row1 in self.data
            ]
        )
        Matrix.cached_matmul[hash((self, other))] = copy.deepcopy(res)
        return res

    def __hash__(self):
        # hash = sum of elements hashes
        return sum(sum(hash(x) for x in row) for row in self.data)


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
    try:
        os.mkdir("artifacts/hard")
    except OSError as _:
        pass

    # easy part
    with open("artifacts/easy/matrix+.txt", "w") as file:
        print_matrix(A + B, file=file)
    with open("artifacts/easy/matrix*.txt", "w") as file:
        print_matrix(A * B, file=file)
    with open("artifacts/easy/matrix@.txt", "w") as file:
        print_matrix(A @ B, file=file)

    # hard part
    A = Matrix([[1, 0], [0, 1]])
    B = A
    C = Matrix([[0, 1], [1, 0]])
    D = A

    with open("artifacts/hard/A.txt", "w") as file:
        print_matrix(A, file=file)
    with open("artifacts/hard/B.txt", "w") as file:
        print_matrix(B, file=file)
    with open("artifacts/hard/C.txt", "w") as file:
        print_matrix(C, file=file)
    with open("artifacts/hard/D.txt", "w") as file:
        print_matrix(D, file=file)

    with open("artifacts/hard/AB.txt", "w") as file:
        print_matrix(A @ B, file=file)
    with open("artifacts/hard/hash.txt", "w") as file:
        print(hash(A @ B), file=file)

    Matrix.cached_matmul = {}  # drop caches to obtain true C @ D
    
    with open("artifacts/hard/CD.txt", "w") as file:
        print_matrix(C @ D, file=file)
    with open("artifacts/hard/hash.txt", "a") as file:
        print(hash(C @ D), file=file)
    with open("artifacts/hard/AB_wrong.txt", "w") as file:
        print_matrix(A @ B, file=file)
    
    print(hash(A), hash(B), hash(C), hash(D))
    print(hash((A, B)), hash(((C, D))))
