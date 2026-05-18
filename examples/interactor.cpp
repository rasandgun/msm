#include <bits/stdc++.h>
using namespace std;

int main(int argc, char** argv) {
    unsigned long long seed = strtoull(argv[1], nullptr, 10);
    srand(seed);
    int n = rand() % 100;
    cout << n << endl;
    int x = rand() % (n + 1);
    while (true) {
        int r;
        cin >> r;
        if (r < x)
            cout << -1 << endl;
        else if (r == x) {
            cout << 0 << endl;
            return 0;
        } else {
            cout << 1 << endl;
        }
    }
    return -1;
}