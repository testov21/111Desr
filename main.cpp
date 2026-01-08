#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int N, S, L, M, K, P;
    cin >> N >> S >> L >> M >> K >> P;

    int sp = S / P;
    int ppg = sp * K;
    int R = N * ppg;
    int oxcs_per_plane = M / P;

    vector<vector<array<int, 4>>> qs(5);
    vector<vector<int>> max_demand(N, vector<int>(N, 0));
    
    for (int qi = 0; qi < 5; qi++) {
        int Q; cin >> Q;
        qs[qi].resize(Q);
        vector<vector<int>> qd(N, vector<int>(N, 0));
        for (int i = 0; i < Q; i++) {
            cin >> qs[qi][i][0] >> qs[qi][i][1] >> qs[qi][i][2] >> qs[qi][i][3];
            int a = qs[qi][i][0], b = qs[qi][i][2];
            if (a > b) swap(a, b);
            qd[a][b]++;
        }
        for (int a = 0; a < N; a++)
            for (int b = a + 1; b < N; b++)
                max_demand[a][b] = max(max_demand[a][b], qd[a][b]);
    }

    vector<int> arr(N);
    iota(arr.begin(), arr.end(), 0);
    vector<vector<pair<int,int>>> rounds;
    for (int r = 0; r < N - 1; r++) {
        vector<pair<int,int>> ps;
        for (int i = 0; i < N / 2; i++) {
            int x = arr[i], y = arr[N - 1 - i];
            if (x > y) swap(x, y);
            ps.push_back({x, y});
        }
        rounds.push_back(ps);
        int last = arr[N - 2];
        for (int i = N - 2; i >= 1; i--) arr[i] = arr[i - 1];
        arr[0] = last;
    }

    double ratio = (double)(oxcs_per_plane * K) / (double)L;
    struct Opt { int m, offA, offB; };

    auto build_and_score = [&](uint64_t seed) {
        mt19937_64 rng(seed);

        vector<int> round_demand(N - 1, 0);
        for (int r = 0; r < N - 1; r++)
            for (auto [u, v] : rounds[r])
                round_demand[r] = max(round_demand[r], max_demand[u][v]);

        int total_slots = M * ppg;
        vector<int> slot_count(N - 1, 1);
        long long total = 0;
        for (int r = 0; r < N - 1; r++) total += round_demand[r] + 1;
        
        int remaining = total_slots - (N - 1);
        for (int r = 0; r < N - 1; r++)
            slot_count[r] += (int)((long long)remaining * (round_demand[r] + 1) / total);
        
        vector<int> slot_round;
        for (int r = 0; r < N - 1; r++)
            for (int i = 0; i < slot_count[r]; i++)
                slot_round.push_back(r);
        
        while ((int)slot_round.size() < total_slots) {
            int best = 0;
            for (int r = 1; r < N - 1; r++)
                if (round_demand[r] > round_demand[best]) best = r;
            slot_round.push_back(best);
        }
        shuffle(slot_round.begin(), slot_round.end(), rng);

        vector<vector<int>> perm(N, vector<int>(ppg));
        for (int g = 0; g < N; g++) {
            iota(perm[g].begin(), perm[g].end(), 0);
            shuffle(perm[g].begin(), perm[g].end(), rng);
        }

        vector<vector<int>> cfg(M, vector<int>(R, -1));
        vector<vector<vector<Opt>>> opt(N, vector<vector<Opt>>(N));

        int si = 0;
        for (int m = 0; m < M && si < total_slots; m++) {
            for (int base = 0; base < ppg && si < total_slots; base++, si++) {
                int r = slot_round[si];
                for (auto [u, v] : rounds[r]) {
                    int offU = perm[u][base];
                    int offV = perm[v][base];
                    cfg[m][u * ppg + offU] = v * ppg + offV;
                    cfg[m][v * ppg + offV] = u * ppg + offU;
                    opt[u][v].push_back({m, offU, offV});
                }
            }
        }

        double total_score = 0;
        for (int qi = 0; qi < 5; qi++) {
            int Q = (int)qs[qi].size();
            vector<int> deg(N * L, 0);
            for (auto& f : qs[qi]) {
                deg[f[0] * L + f[1]]++;
                deg[f[2] * L + f[3]]++;
            }
            vector<int> order(Q);
            iota(order.begin(), order.end(), 0);
            stable_sort(order.begin(), order.end(), [&](int i, int j) {
                auto& a = qs[qi][i]; auto& b = qs[qi][j];
                return deg[a[0]*L+a[1]] + deg[a[2]*L+a[3]] > deg[b[0]*L+b[1]] + deg[b[2]*L+b[3]];
            });
            vector<int> ls(N * L * S, 0);
            vector<int> so((size_t)N * S * M * K, 0);
            vector<int> pu((size_t)M * R, 0);
            int max_conf = 1;
            for (int ii = 0; ii < Q; ii++) {
                int id = order[ii];
                auto& f = qs[qi][id];
                int gA = f[0], leafA = f[1], gB = f[2], leafB = f[3];
                int u = gA, v = gB;
                bool sw = u > v;
                if (sw) swap(u, v);
                auto& vec = opt[u][v];
                int best_cost = INT_MAX, best_sum = INT_MAX;
                int bm = 0, bsA = 0, bsB = 0, bkA = 0, bkB = 0;
                for (auto& e : vec) {
                    int m = e.m, plane = m / oxcs_per_plane;
                    int offA = e.offA, offB = e.offB;
                    int spA = plane * sp + offA / K, spB = plane * sp + offB / K;
                    int kA = offA % K, kB = offB % K;
                    if (sw) { swap(spA, spB); swap(kA, kB); swap(offA, offB); }
                    int lA = ls[(gA * L + leafA) * S + spA] + 1;
                    int lB = ls[(gB * L + leafB) * S + spB] + 1;
                    int sA = so[((size_t)(gA * S + spA) * M + m) * K + kA] + 1;
                    int sB = so[((size_t)(gB * S + spB) * M + m) * K + kB] + 1;
                    int pA = pu[(size_t)m * R + gA * ppg + offA] + 1;
                    int pB = pu[(size_t)m * R + gB * ppg + offB] + 1;
                    int cost = max({lA, lB, sA, sB, pA, pB});
                    int sum = lA + lB + sA + sB + pA + pB;
                    if (cost < best_cost || (cost == best_cost && sum < best_sum)) {
                        best_cost = cost; best_sum = sum;
                        bm = m; bsA = spA; bsB = spB; bkA = kA; bkB = kB;
                    }
                }
                ls[(gA * L + leafA) * S + bsA]++;
                ls[(gB * L + leafB) * S + bsB]++;
                so[((size_t)(gA * S + bsA) * M + bm) * K + bkA]++;
                so[((size_t)(gB * S + bsB) * M + bm) * K + bkB]++;
                int plane = bm / oxcs_per_plane;
                int oA = (bsA - plane * sp) * K + bkA;
                int oB = (bsB - plane * sp) * K + bkB;
                pu[(size_t)bm * R + gA * ppg + oA]++;
                pu[(size_t)bm * R + gB * ppg + oB]++;
                max_conf = max(max_conf, best_cost);
            }
            total_score += 1000.0 / (max_conf * ratio);
        }
        return make_pair(total_score, make_pair(cfg, opt));
    };

    vector<vector<int>> best_cfg;
    vector<vector<vector<Opt>>> best_opt;
    double best_score = -1;
    auto start = chrono::steady_clock::now();
    for (int it = 0; it < 500; it++) {
        if (chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - start).count() > 4500) break;
        auto [score, result] = build_and_score(it * 1234567891ULL + 42);
        if (score > best_score) { best_score = score; best_cfg = move(result.first); best_opt = move(result.second); }
    }

    for (int qi = 0; qi < 5; qi++) {
        int Q = (int)qs[qi].size();
        vector<int> deg(N * L, 0);
        for (auto& f : qs[qi]) { deg[f[0] * L + f[1]]++; deg[f[2] * L + f[3]]++; }
        vector<int> order(Q);
        iota(order.begin(), order.end(), 0);
        stable_sort(order.begin(), order.end(), [&](int i, int j) {
            auto& a = qs[qi][i]; auto& b = qs[qi][j];
            return deg[a[0]*L+a[1]] + deg[a[2]*L+a[3]] > deg[b[0]*L+b[1]] + deg[b[2]*L+b[3]];
        });
        vector<int> ls(N * L * S, 0);
        vector<int> so((size_t)N * S * M * K, 0);
        vector<int> pu((size_t)M * R, 0);
        vector<array<int, 5>> routes(Q);
        for (int ii = 0; ii < Q; ii++) {
            int id = order[ii];
            auto& f = qs[qi][id];
            int gA = f[0], leafA = f[1], gB = f[2], leafB = f[3];
            int u = gA, v = gB;
            bool sw = u > v;
            if (sw) swap(u, v);
            auto& vec = best_opt[u][v];
            int best_cost = INT_MAX, best_sum = INT_MAX;
            int bm = 0, bsA = 0, bsB = 0, bkA = 0, bkB = 0;
            for (auto& e : vec) {
                int m = e.m, plane = m / oxcs_per_plane;
                int offA = e.offA, offB = e.offB;
                int spA = plane * sp + offA / K, spB = plane * sp + offB / K;
                int kA = offA % K, kB = offB % K;
                if (sw) { swap(spA, spB); swap(kA, kB); swap(offA, offB); }
                int lA = ls[(gA * L + leafA) * S + spA] + 1;
                int lB = ls[(gB * L + leafB) * S + spB] + 1;
                int sA = so[((size_t)(gA * S + spA) * M + m) * K + kA] + 1;
                int sB = so[((size_t)(gB * S + spB) * M + m) * K + kB] + 1;
                int pA = pu[(size_t)m * R + gA * ppg + offA] + 1;
                int pB = pu[(size_t)m * R + gB * ppg + offB] + 1;
                int cost = max({lA, lB, sA, sB, pA, pB});
                int sum = lA + lB + sA + sB + pA + pB;
                if (cost < best_cost || (cost == best_cost && sum < best_sum)) {
                    best_cost = cost; best_sum = sum;
                    bm = m; bsA = spA; bsB = spB; bkA = kA; bkB = kB;
                }
            }
            ls[(gA * L + leafA) * S + bsA]++;
            ls[(gB * L + leafB) * S + bsB]++;
            so[((size_t)(gA * S + bsA) * M + bm) * K + bkA]++;
            so[((size_t)(gB * S + bsB) * M + bm) * K + bkB]++;
            int plane = bm / oxcs_per_plane;
            int oA = (bsA - plane * sp) * K + bkA;
            int oB = (bsB - plane * sp) * K + bkB;
            pu[(size_t)bm * R + gA * ppg + oA]++;
            pu[(size_t)bm * R + gB * ppg + oB]++;
            routes[id] = {bsA, bkA, bm, bsB, bkB};
        }
        for (int m = 0; m < M; m++)
            for (int p = 0; p < R; p++)
                cout << best_cfg[m][p] << (p + 1 == R ? '\n' : ' ');
        for (auto& r : routes)
            cout << r[0] << ' ' << r[1] << ' ' << r[2] << ' ' << r[3] << ' ' << r[4] << '\n';
    }
    return 0;
}
