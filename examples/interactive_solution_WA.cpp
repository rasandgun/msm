#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    int l = -1, r = n;
    while (r - l > 1) {
        int m = (l + r) >> 1;
        cout << m << endl;
        int x;
        cin >> x;
        if (x == 0) return 0;
        if (x == 1)
            r = m;
        else
            l = m;
    }
    return 0;
}