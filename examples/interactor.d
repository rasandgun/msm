import std.stdio;
import std.conv;
import std.random;
import std.c.stdlib;

void main(string[] args) {
    ulong seed = args[1].to!ulong;
    srand(seed);
    
    int n = rand() % 100;
    writeln(n);
    
    int x = rand() % (n + 1);
    
    while (true) {
        int r;
        readf("%d", &r);
        
        if (r < x)
            writeln(-1);
        else if (r == x) {
            writeln(0);
            return;
        } else
            writeln(1);
    }
}