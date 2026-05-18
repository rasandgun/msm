import std.stdio;
import std.conv;
import std.random;
import std.string;
void main(string[] args) {
    ulong seed = args[1].to!ulong;
    rndGen.seed(cast(uint)seed);
    int n = uniform(0, 100);
    writeln(n);
    stdout.flush;
    int x = uniform(0, n + 1);
    while (true) {
        auto r = readln.strip.to!int;
        if (r < x)
            writeln(-1);
        else if (r == x) {
            writeln(0);
            return;
        } else
            writeln(1);
        stdout.flush;
    }
}