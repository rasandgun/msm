#include <iostream>
#include <vector>
#include <algorithm>
#include <ctime>
#include <cassert>
#include <cmath>
#include <random>
#include <bitset>
using namespace std;
constexpr int MAXN = 51;
constexpr int MAXK = 101;

int current_query;
int a[MAXN][MAXN];
bool deleted[MAXN][MAXN];
bool used[MAXN][MAXN];
int se[MAXN][MAXN];
bool bonus1000 = true;
using ll = long long;
ll ans = 0;
int n, m;

inline bool to_be_deleted_ver(int i, int j) {
    if (a[i][j] == 0) return false;
    if (j >= 2 && a[i][j - 2] == a[i][j - 1] && a[i][j - 1] == a[i][j]) {
        return true;
    }
    if (j + 1 < m && j - 1 >= 0 && a[i][j - 1] == a[i][j] && a[i][j] == a[i][j + 1]) {
        return true;
    }
    if (j < m - 2 && a[i][j + 2] == a[i][j + 1] && a[i][j] == a[i][j + 1]) {
        return true;
    }
    return false;
}

inline bool to_be_deleted_hor(int i, int j) {
    if (a[i][j] == 0) return false;
    if (i >= 2 && a[i - 2][j] == a[i - 1][j] && a[i - 1][j] == a[i][j]) {
        return true;
    }
    if (i + 1 < n && i - 1 >= 0 && a[i - 1][j] == a[i][j] && a[i][j] == a[i + 1][j]) {
        return true;
    }
    if (i < n - 2 && a[i + 2][j] == a[i + 1][j] && a[i][j] == a[i + 1][j]) {
        return true;
    }
    return false;
}

inline bool to_be_deleted(int i, int j) {
    if (a[i][j] == 0) return false;
    return to_be_deleted_hor(i, j) || to_be_deleted_ver(i, j);
}

bool chain_iteration() {
    bool res = false;
    for (int j = 0; j < m; j++) {
        for (int i = 0; i < n; i++) {
            if (to_be_deleted_hor(i, j) || to_be_deleted_ver(i, j)) {
                res = true;
                deleted[i][j] = true;
            }
        }
    }
    return res;
}



int dfs(int i, int j) {
    int res = 1;
    used[i][j] = true;
    if (i >= 1 && a[i][j] == a[i - 1][j] && deleted[i - 1][j] && !used[i - 1][j])
        res += dfs(i - 1, j);
    if (i < n - 1 && a[i][j] == a[i + 1][j] && deleted[i + 1][j] && !used[i + 1][j])
        res += dfs(i + 1, j);
    if (j >= 1 && a[i][j] == a[i][j - 1] && deleted[i][j - 1] && !used[i][j - 1])
        res += dfs(i, j - 1);
    if (j < m - 1 && a[i][j] == a[i][j + 1] && deleted[i][j + 1] && !used[i][j + 1])
        res += dfs(i, j + 1);
    return res;
}

void gravity() {
    for (int j = 0; j < m; j++) {
        int last = n - 1;
        for (int i = n - 1; i >= 0; i--) {
            if (a[i][j] != 0) {
                swap(a[i][j], a[last][j]);
                swap(se[i][j], se[last][j]);
                last--;
            }
        }
    }
}


void special_effects(int i, int j) {
    used[i][j] = true;
    if (se[i][j] == 0) return;
    switch (se[i][j])  {
    case 0:
        assert(false);
        break;
    case 1:
        for (int z = 0; z < m; z++) {
            if (!used[i][z] && a[i][z] != 0) {
                deleted[i][z] = true;
                special_effects(i, z);
            }
        }
        break;
    case 2:
        for (int z = 0; z < n; z++) {
            if (!used[z][j] && a[z][j] != 0) {
                deleted[z][j] = true;
                special_effects(z, j);
            }
        }
        break;
    case 3:
        for (int z = 0; z < n; z++) {
            if (!used[z][j] && a[z][j] != 0) {
                deleted[z][j] = true;
                special_effects(z, j);
            }
        }
        for (int z = 0; z < m; z++) {
            if (!used[i][z] && a[i][z] != 0) {
                deleted[i][z] = true;
                special_effects(i, z);
            }
        }
        break;
    case 4:
        for (int k = max(0, i - 1); k <= min(n - 1, i + 1); k++)
            for (int z = max(0, j - 1); z <= min(m - 1, j + 1); z++) {
                if (!used[k][z] && a[k][z] != 0) {
                    deleted[k][z] = true;
                    special_effects(k, z);
                }
            }
        break;
    case 5:
        for (int k = max(0, i - 2); k <= min(n - 1, i + 2); k++)
            for (int z = max(0, j - 2); z <= min(m - 1, j + 2); z++) {
                if (!used[k][z]) {
                    deleted[k][z] = true;
                    special_effects(k, z);
                }
            }
        break;
    case 6:
        for (int k = 0; k < n; k++) {
            for (int z = 0; z < m; z++) {
                if (a[k][z] == a[i][j] && !used[k][z]) {
                    deleted[k][z] = true;
                    special_effects(k, z);
                }
            }
        }
        break;
    default:
        assert(false);
    }
}

int apply_deleted() {
    int res = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            if (deleted[i][j]) {
                res += a[i][j];
                a[i][j] = 0;
                se[i][j] = 0;
            }
        }
    }
    return res;
}

void print(int arr[][MAXN]) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < m; j++) {
            cout << arr[i][j] << " ";
        }
        cout << "\n";
    }
    cout << "----\n";
}

inline ll sq(int x) {
    return x * 1ll * x;
}

inline ll func(int x) {
    if (x < 3) return 0;
    return (x - 3) * 50ll * (x - 3);
}

struct operation_result {
    int first_col, second_col;
};

vector<operation_result> poker_colors;


operation_result operation(int i1, int j1, int i2, int j2) {
    operation_result res;
    if (a[i1][j1] == 0 || a[i2][j2] == 0) return {-1, -1};
    swap(a[i1][j1], a[i2][j2]);
    swap(se[i1][j1], se[i2][j2]);
    if (to_be_deleted(i1, j1)) {
        res.first_col = a[i1][j1];
        if (to_be_deleted(i2, j2))
            res.second_col = a[i2][j2];
        else
            res.second_col = a[i1][j1];
    } else {
        if (to_be_deleted(i2, j2))
            res.first_col = res.second_col = a[i2][j2];
        else {
            swap(a[i1][j1], a[i2][j2]);
            swap(se[i1][j1], se[i2][j2]);
            return {-1, -1};
        }
    }
    int iteraion = 1;
    while (chain_iteration()) {
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (!used[i][j] && deleted[i][j])
                    ans += func(dfs(i, j));
            }
        }
        for (int i = 0; i < n; i++)
            fill(used[i], used[i] + m, false);
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m; j++) {
                if (!used[i][j] && deleted[i][j] && a[i][j] != 0) {
                    special_effects(i, j);
                }
            }
        }
        for (int i = 0; i < n; i++)
            fill(used[i], used[i] + m, false);
        int x = apply_deleted();
        ans += iteraion * 1ll * x;
        gravity();
        iteraion++;
        for (int i = 0; i < n; i++)
            fill(deleted[i], deleted[i] + m, false);
        for (int i = 0; i < n; i++)
            fill(used[i], used[i] + m, false);
    }
    assert(iteraion != 1);
    ans += 80 * sq(iteraion - 2);
    return res;
}

int poker(int mask) {
    int colors[5];
    for (int i = 0; i < 5; i++) {
        if ((mask >> i) & 1)
            colors[i] = poker_colors[i].first_col;
        else
            colors[i] = poker_colors[i].second_col;
    }
    sort(colors, colors + 5, greater<int>());
    if (colors[0] == colors[1] && colors[1] == colors[2] && colors[2] == colors[3] && colors[3] == colors[4])
        return 1000 + colors[0] * 10;
    if (colors[0] == colors[1] && colors[1] == colors[2] && colors[2] == colors[3])
        return 750 + colors[0] * 5;
    if (colors[1] == colors[2] && colors[2] == colors[3] && colors[3] == colors[4])
        return 750 + colors[1] * 5;
    if (colors[0] == colors[1] && colors[1] == colors[2] && colors[3] == colors[4])
        return 500 + colors[0] * 3 + colors[3];
    if (colors[0] == colors[1] && colors[2] == colors[3] && colors[3] == colors[4])
        return 500 + colors[2] * 3 + colors[0];
    if (colors[0] == colors[1] && colors[1] == colors[2])
        return 300 + colors[0] * 3;
    if (colors[1] == colors[2] && colors[2] == colors[3])
        return 300 + colors[1] * 3;
    if (colors[2] == colors[3] && colors[3] == colors[4])
        return 300 + colors[2] * 3;
    if (colors[0] == colors[1] && colors[2] == colors[3])
        return 200 + colors[0] * 2 + colors[2];
    if (colors[0] == colors[1] && colors[3] == colors[4])
        return 200 + colors[0] * 2 + colors[3];
    if (colors[1] == colors[2] && colors[3] == colors[4])
        return 200 + colors[1] * 2 + colors[3];
    if (colors[0] == colors[1])
        return 100 + colors[0] * 2;
    if (colors[1] == colors[2])
        return 100 + colors[1] * 2;
    if (colors[2] == colors[3])
        return 100 + colors[2] * 2;
    if (colors[3] == colors[4])
        return 100 + colors[3] * 2;
    return 50 + colors[0];
}



signed main() {
    ios_base::sync_with_stdio(false);
    cin.tie(nullptr);
    int k, q;
    cin >> n >> m >> k >> q;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> a[i][j];
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            cin >> se[i][j];
    for (current_query = 0; current_query < q; current_query++) {
        int i1, j1, i2, j2;
        cin >> i1 >> j1 >> i2 >> j2;;
        i1--, j1--, i2--, j2--;
        if (abs(i2 - i1) + abs(j2 - j1) != 1) {
            bonus1000 = false;
            continue;
        }
        auto [fc, sc] = operation(i1, j1, i2, j2);
        cout << fc <<  " " << sc << endl; 
        if (fc == -1) {
            bonus1000 = false;
            continue;
        }
        poker_colors.push_back({fc, sc});
        bool poker_check = poker_colors.size() >= 5;
        for (int i = 0; i < poker_colors.size(); i++) {
            if (poker_colors[i].first_col == -1)
                poker_check = false;
        }
        if (poker_check) {
            int mx = 0;
            for (int mask = 0; mask < (1 << 5); mask++) {
                int xxx = poker(mask);
                if (mx < xxx) {
                    mx = xxx;
                }
            }
            poker_colors.clear();
            ans += mx;
        }
    }
    if (bonus1000) {
        ans += 1000;
    }
    bool bonus10000 = true;
    for (int i = 0; i < n; i++)
        for (int j = 0; j < m; j++)
            if (a[i][j] != 0)
                bonus10000 = false;
    if (bonus10000)
        ans += 10000;
    cout << ans << "\n";
    return 0;
}
