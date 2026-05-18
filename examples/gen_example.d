import std.stdio;
import std.random;
import std.range;
import std.algorithm;
import std.array;
import std.datetime;
import std.typecons;

void main() {
    auto rng = Xorshift(cast(uint)Clock.currTime().nsecs);
    
    
    auto params = generateParams(rng);
    int n = params[0];
    int m = params[1];
    int k = params[2];
    int q = params[3];
    
    writefln("%d %d %d %d", n, m, k, q);
    
    
    auto a = generateMatrix(n, m, k, rng);
    foreach (row; a) {
        writeRow(row);
    }
    
    
    foreach (i; 0..n) {
        writeZeroRow(m);
    }
    
    
    foreach (i; 0..q) {
        auto swap = generateSingleSwap(n, m, rng);
        writeSwap(swap);
    }
}


auto generateParams(ref Xorshift rng) {
    return tuple(
        uniform!"[]"(4, 15, rng),  
        uniform!"[]"(4, 15, rng),  
        uniform!"[]"(3, 4, rng),   
        uniform!"[]"(3, 15, rng)   
    );
}


auto generateMatrix(int n, int m, int k, ref Xorshift rng) {
    auto matrix = new int[][](n, m);
    foreach (i; 0..n) {
        foreach (j; 0..m) {
            matrix[i][j] = uniform!"[]"(1, k, rng);
        }
    }
    return matrix;
}


void writeRow(int[] row) {
    foreach (i, val; row) {
        if (i > 0) write(' ');
        write(val);
    }
    writeln();
}


void writeZeroRow(int m) {
    foreach (j; 0..m) {
        if (j > 0) write(' ');
        write('0');
    }
    writeln();
}


auto generateSingleSwap(int n, int m, ref Xorshift rng) {
    while (true) {
        int x1 = uniform!"[]"(1, n, rng);
        int y1 = uniform!"[]"(1, m, rng);
        
        
        int dx, dy;
        if (uniform(0, 2, rng) == 0) {
            dx = uniform!"[]"(-1, 1, rng);  
            dy = 0;
        } else {
            dx = 0;
            dy = uniform!"[]"(-1, 1, rng);  
        }
        
        int x2 = x1 + dx;
        int y2 = y1 + dy;
        
        if (x2 >= 1 && x2 <= n && y2 >= 1 && y2 <= m) {
            return tuple(x1, y1, x2, y2);
        }
    }
}


void writeSwap(Tuple!(int, int, int, int) swap) {
    writefln("%d %d %d %d", swap[0], swap[1], swap[2], swap[3]);
}