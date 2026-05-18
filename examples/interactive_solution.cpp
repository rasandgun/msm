#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    int l = 0, r = n + 1;
    while (l <= r) {
        int m = (l + r) / 2;
        cout << m << endl;
        int x;
        cin >> x;
        if (x == 0) return 0;
        if (x == -1) {  
            l = m + 1;
        } else {
            r = m - 1;
        }
    }
    return 0;
}