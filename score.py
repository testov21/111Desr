import argparse
import sys


def parse_ints(s: str):
    return list(map(int, s.split()))


def read_all(path: str | None) -> str:
    if path is None or path == "-":
        return sys.stdin.read()
    data = open(path, "rb").read()
    if data.startswith(b"\xff\xfe"):
        return data[2:].decode("utf-16-le", errors="strict")
    if data.startswith(b"\xfe\xff"):
        return data[2:].decode("utf-16-be", errors="strict")
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:].decode("utf-8", errors="strict")
    try:
        return data.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def score_instance(inp: str, out: str, alpha: int):
    it = iter(inp.split())
    N = int(next(it)); S = int(next(it)); L = int(next(it))
    M = int(next(it)); K = int(next(it)); P = int(next(it))
    sp = S // P
    ports_per_group = sp * K
    R = N * ports_per_group
    oxcs_per_plane = M // P

    tok = out.split()
    idx = 0

    def need(n: int, msg: str):
        nonlocal idx
        if idx + n > len(tok):
            raise ValueError(msg)

    def read_cfg():
        nonlocal idx
        cfg = [[-1] * R for _ in range(M)]
        need(M * R, "short topology")
        for m in range(M):
            row = cfg[m]
            for p in range(R):
                row[p] = int(tok[idx]); idx += 1
        return cfg

    def cfg_ok(cfg):
        for m in range(M):
            row = cfg[m]
            for p in range(R):
                v = row[p]
                if v == -1:
                    continue
                if not (0 <= v < R):
                    return False, ("bad port", m, p, v)
                if v == p:
                    return False, ("self loop", m, p)
                if row[v] != p:
                    return False, ("not symmetric", m, p, v, row[v])
        return True, ("ok",)

    def edge_count(cfg):
        c = 0
        for m in range(M):
            row = cfg[m]
            for p in range(R):
                v = row[p]
                if v != -1 and p < v:
                    c += 1
        return c

    def common_edges(a, b):
        if a is None:
            return 0
        c = 0
        for m in range(M):
            ra = a[m]
            rb = b[m]
            for p in range(R):
                v = ra[p]
                if v != -1 and p < v and rb[p] == v and rb[v] == p:
                    c += 1
        return c

    def adjust_cost(prev, cur):
        ecur = edge_count(cur)
        if prev is None:
            return ecur
        eprev = edge_count(prev)
        com = common_edges(prev, cur)
        return eprev + ecur - 2 * com

    def port(g, s, k):
        return g * ports_per_group + (s % sp) * K + k

    def idx_leaf(g, leaf, s):
        return (g * L + leaf) * S + s

    def idx_spoxc(g, s, m, k):
        return (((g * S + s) * M) + m) * K + k

    ratio = ((M // P) * K) / L
    if ratio == 0:
        ratio = 1e-9

    per_query = []
    total_points = 0.0
    prev_cfg = None

    for q in range(5):
        cfg = read_cfg()
        ok, msg = cfg_ok(cfg)
        if not ok:
            raise ValueError(f"invalid topology q={q}: {msg}")

        Q = int(next(it))
        flows = []
        for _ in range(Q):
            gA = int(next(it)); leafA = int(next(it)); gB = int(next(it)); leafB = int(next(it))
            flows.append((gA, leafA, gB, leafB))

        leaf_spine = [0] * (N * L * S)
        sp_oxc = [0] * (N * S * M * K)
        port_use = [0] * (M * R)

        max_ls = 0
        max_so = 0
        max_pu = 0

        need(Q * 5, "short routes")
        for i in range(Q):
            x = int(tok[idx]); kx = int(tok[idx + 1]); m = int(tok[idx + 2]); y = int(tok[idx + 3]); ky = int(tok[idx + 4])
            idx += 5
            if not (0 <= x < S and 0 <= y < S and 0 <= m < M and 0 <= kx < K and 0 <= ky < K):
                raise ValueError(f"route range q={q} i={i}")
            if x // sp != m // oxcs_per_plane or y // sp != m // oxcs_per_plane:
                raise ValueError(f"plane mismatch q={q} i={i}")

            gA, leafA, gB, leafB = flows[i]
            pA = port(gA, x, kx)
            pB = port(gB, y, ky)
            if cfg[m][pA] != pB or cfg[m][pB] != pA:
                raise ValueError(f"no connection q={q} i={i} flow={flows[i]} route={(x,kx,m,y,ky)} ports={(pA,pB)} cfg={(cfg[m][pA],cfg[m][pB])}")

            a = idx_leaf(gA, leafA, x)
            b = idx_leaf(gB, leafB, y)
            leaf_spine[a] += 1
            leaf_spine[b] += 1
            if leaf_spine[a] > max_ls:
                max_ls = leaf_spine[a]
            if leaf_spine[b] > max_ls:
                max_ls = leaf_spine[b]

            a2 = idx_spoxc(gA, x, m, kx)
            b2 = idx_spoxc(gB, y, m, ky)
            sp_oxc[a2] += 1
            sp_oxc[b2] += 1
            if sp_oxc[a2] > max_so:
                max_so = sp_oxc[a2]
            if sp_oxc[b2] > max_so:
                max_so = sp_oxc[b2]

            pi = m * R + pA
            pj = m * R + pB
            port_use[pi] += 1
            port_use[pj] += 1
            if port_use[pi] > max_pu:
                max_pu = port_use[pi]
            if port_use[pj] > max_pu:
                max_pu = port_use[pj]

        conf = max(max_ls, max_so, max_pu)
        adj = adjust_cost(prev_cfg, cfg)
        prev_cfg = cfg
        a = 1000.0
        b = 300.0
        points = a / (conf * ratio) + b * (1.0 - (adj / (M * R)))
        per_query.append((conf, adj, points))
        total_points += points

    return {
        "N": N, "S": S, "L": L, "M": M, "K": K, "P": P,
        "ratio": ratio,
        "per_query": per_query,
        "total_points": total_points,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", default="-")
    ap.add_argument("--output", "-o", default="-")
    ap.add_argument("--alpha", type=int, default=0)
    args = ap.parse_args()

    inp = read_all(args.input)
    out = read_all(args.output)
    res = score_instance(inp, out, args.alpha)

    print(f"N={res['N']} S={res['S']} L={res['L']} M={res['M']} K={res['K']} P={res['P']}")
    print(f"ratio={res['ratio']}")
    for i, (c, a, pts) in enumerate(res["per_query"]):
        print(f"q{i+1}: conf={c} adj={a} pts={pts}")
    print(f"TOTAL={res['total_points']}")


if __name__ == "__main__":
    main()

