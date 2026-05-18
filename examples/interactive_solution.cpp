#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    int l = -1, r = n + 1;
    while (r - l > 1) {
        int m = (l + r) / 2;
        cout << m << endl;
        int x;
        cin >> x;
        if (x == 0) return 0;
        if (x == -1) {  
            l = m;
        } else {
            r = m;
        }
    }
    return 0;
}