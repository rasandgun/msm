#include <iostream>
#include <random>
#include <vector>

using namespace std;

int main() {
    
    random_device rd;
    mt19937 gen(rd());

    
    uniform_int_distribution<> dist_n(4, 15);
    uniform_int_distribution<> dist_m(4, 15);
    uniform_int_distribution<> dist_k(3, 4);
    uniform_int_distribution<> dist_q(3, 15);

    
    int n, m;
    n = dist_n(gen);
    m = dist_m(gen);
    int k = dist_k(gen);
    int q = dist_q(gen);

    
    cout << n << " " << m << " " << k << " " << q << "\n";

    
    uniform_int_distribution<> color_dist(1, k);
    uniform_int_distribution<> effect_dist(0, 0);

    
    vector<vector<int>> a(n, vector<int>(m));
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            a[i][j] = color_dist(gen);
            cout << a[i][j] << " ";
        }
        cout << "\n";
    }

    
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < m; ++j) {
            cout << effect_dist(gen) << " ";
        }
        cout << "\n";
    }

    
    uniform_int_distribution<> coord_x(1, n);
    uniform_int_distribution<> coord_y(1, m);

    
    for (int i = 0; i < q; ++i) {
        int x1, y1, x2, y2;
        do {
            x1 = coord_x(gen);
            y1 = coord_y(gen);
            x2 = x1 + (rand() % 3) - 1;
            y2 = y1 + (rand() % 3) - 1;
        } while (abs(x1 - x2) + abs(y1 - y2) != 1); 
        cout << x1 << " " << y1 << " " << x2 << " " << y2 << "\n";
    }

    return 0;
}