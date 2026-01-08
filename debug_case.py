import pathlib
import subprocess


def check(inp: str, out: str):
    it = iter(inp.split())
    N = int(next(it)); S = int(next(it)); L = int(next(it))
    M = int(next(it)); K = int(next(it)); P = int(next(it))
    sp = S // P
    ports_per_group = sp * K
    R = N * ports_per_group
    oxcs_per_plane = M // P

    tok = out.split()
    idx = 0

    for q in range(5):
        cfg = [[-1] * R for _ in range(M)]
        for m in range(M):
            for p in range(R):
                cfg[m][p] = int(tok[idx]); idx += 1

        for m in range(M):
            for p in range(R):
                v = cfg[m][p]
                if v == -1:
                    continue
                if not (0 <= v < R):
                    return ("bad port", q, m, p, v)
                if v == p:
                    return ("self", q, m, p, v)
                if cfg[m][v] != p:
                    return ("not sym", q, m, p, v, cfg[m][v])

        Q = int(next(it))
        flows = []
        for _ in range(Q):
            gA = int(next(it)); leafA = int(next(it)); gB = int(next(it)); leafB = int(next(it))
            flows.append((gA, leafA, gB, leafB))

        for i in range(Q):
            x = int(tok[idx]); kx = int(tok[idx + 1]); m = int(tok[idx + 2]); y = int(tok[idx + 3]); ky = int(tok[idx + 4])
            idx += 5
            if not (0 <= x < S and 0 <= y < S and 0 <= m < M and 0 <= kx < K and 0 <= ky < K):
                return ("route range", q, i, (x, kx, m, y, ky))
            if x // sp != m // oxcs_per_plane or y // sp != m // oxcs_per_plane:
                return ("plane mismatch", q, i, (x, kx, m, y, ky))

            gA, leafA, gB, leafB = flows[i]
            portA = gA * ports_per_group + (x % sp) * K + kx
            portB = gB * ports_per_group + (y % sp) * K + ky
            if cfg[m][portA] != portB or cfg[m][portB] != portA:
                return ("no conn", q, i, (gA, leafA, gB, leafB), (x, kx, m, y, ky), (portA, portB), (cfg[m][portA], cfg[m][portB]))

    return ("ok",)


def main():
    inp = pathlib.Path("fail_case.txt").read_text(encoding="utf-8")
    exe = r"C:\Code_Turnament\main.exe"
    p = subprocess.run([exe], input=inp.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = p.stdout.decode()
    res = check(inp, out)
    print(res)


if __name__ == "__main__":
    main()

