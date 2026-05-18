import std.stdio;
import std.random;
import std.range;
import std.algorithm;
import std.array;
import std.datetime;
import std.typecons;

void main() {
    auto rng = Xorshift(cast(uint)Clock.currTime().nsecs);
    
    // Исправлено: без tuple destructuring
    auto params = generateParams(rng);
    int n = params[0];
    int m = params[1];
    int k = params[2];
    int q = params[3];
    
    writefln("%d %d %d %d", n, m, k, q);
    
    // Генерация и вывод матрицы a
    auto a = generateMatrix(n, m, k, rng);
    foreach (row; a) {
        writeRow(row);
    }
    
    // Матрица b (все нули)
    foreach (i; 0..n) {
        writeZeroRow(m);
    }
    
    // Генерация и вывод обменов
    foreach (i; 0..q) {
        auto swap = generateSingleSwap(n, m, rng);
        writeSwap(swap);
    }
}

// Генерация параметров
auto generateParams(ref Xorshift rng) {
    return tuple(
        uniform!"[]"(4, 15, rng),  // n
        uniform!"[]"(4, 15, rng),  // m
        uniform!"[]"(3, 4, rng),   // k
        uniform!"[]"(3, 15, rng)   // q
    );
}

// Генерация матрицы a
auto generateMatrix(int n, int m, int k, ref Xorshift rng) {
    auto matrix = new int[][](n, m);
    foreach (i; 0..n) {
        foreach (j; 0..m) {
            matrix[i][j] = uniform!"[]"(1, k, rng);
        }
    }
    return matrix;
}

// Вывод строки матрицы a
void writeRow(int[] row) {
    foreach (i, val; row) {
        if (i > 0) write(' ');
        write(val);
    }
    writeln();
}

// Вывод строки нулей (матрица b)
void writeZeroRow(int m) {
    foreach (j; 0..m) {
        if (j > 0) write(' ');
        write('0');
    }
    writeln();
}

// Генерация одного корректного обмена
auto generateSingleSwap(int n, int m, ref Xorshift rng) {
    while (true) {
        int x1 = uniform!"[]"(1, n, rng);
        int y1 = uniform!"[]"(1, m, rng);
        
        // Случайное смещение по соседству (только одна из координат меняется)
        int dx, dy;
        if (uniform(0, 2, rng) == 0) {
            dx = uniform!"[]"(-1, 1, rng);  // -1 или 1
            dy = 0;
        } else {
            dx = 0;
            dy = uniform!"[]"(-1, 1, rng);  // -1 или 1
        }
        
        int x2 = x1 + dx;
        int y2 = y1 + dy;
        
        if (x2 >= 1 && x2 <= n && y2 >= 1 && y2 <= m) {
            return tuple(x1, y1, x2, y2);
        }
    }
}

// Вывод обмена
void writeSwap(Tuple!(int, int, int, int) swap) {
    writefln("%d %d %d %d", swap[0], swap[1], swap[2], swap[3]);
}