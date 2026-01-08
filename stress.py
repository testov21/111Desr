import random
import subprocess
import sys
import pathlib


def gen_case(rng: random.Random) -> str:
    while True:
        N = rng.choice([i for i in range(2, 33, 2)])
        S = rng.randint(1, 32)
        L = rng.randint(1, 64)
        if N * S * L > 16384:
            continue

        P = rng.randint(1, min(16, S))
        while S % P != 0:
            P = rng.randint(1, min(16, S))

        K = rng.choice([1, 2])
        M = rng.randint(1, 256)
        while M % P != 0:
            M = rng.randint(1, 256)

        up = (M // P) * K
        if not (up == L or up * 3 == L or up * 7 == L):
            continue
        if (N - 1) > S * (M // P) * K:
            continue
        break

    max_q = (N * S * L) // 2
    lines = [f"{N} {S} {L}", f"{M} {K} {P}"]

    for _ in range(5):
        Q = rng.randint(1, max(1, max_q // 4))
        leaf_cnt = [[0] * L for _ in range(N)]
        flows = []
        for _ in range(Q):
            gA = rng.randrange(N)
            gB = rng.randrange(N)
            while gB == gA:
                gB = rng.randrange(N)
            if gA > gB:
                gA, gB = gB, gA
            leafA = rng.randrange(L)
            leafB = rng.randrange(L)
            if leaf_cnt[gA][leafA] >= S:
                leafA = (leafA + 1) % L
            if leaf_cnt[gB][leafB] >= S:
                leafB = (leafB + 1) % L
            leaf_cnt[gA][leafA] += 1
            leaf_cnt[gB][leafB] += 1
            flows.append((gA, leafA, gB, leafB))
        lines.append(str(Q))
        lines.extend(" ".join(map(str, f)) for f in flows)

    return "\n".join(lines) + "\n"


def check_output(inp: str, out: str) -> tuple[bool, str]:
    it = iter(inp.split())
    N = int(next(it)); S = int(next(it)); L = int(next(it))
    M = int(next(it)); K = int(next(it)); P = int(next(it))
    sp = S // P
    ports_per_group = sp * K
    R = N * ports_per_group

    tok = out.split()
    idx = 0

    oxcs_per_plane = M // P

    for _q in range(5):
        cfg = [[-1] * R for _ in range(M)]
        for m in range(M):
            for p in range(R):
                if idx >= len(tok):
                    return False, "short topology"
                v = int(tok[idx]); idx += 1
                cfg[m][p] = v

        for m in range(M):
            for p in range(R):
                v = cfg[m][p]
                if v == -1:
                    continue
                if not (0 <= v < R):
                    return False, "bad port"
                if v == p:
                    return False, "self loop"
                if cfg[m][v] != p:
                    return False, "not symmetric"

        Q = int(next(it))
        flows = []
        for _ in range(Q):
            gA = int(next(it)); leafA = int(next(it)); gB = int(next(it)); leafB = int(next(it))
            flows.append((gA, leafA, gB, leafB))

        for i in range(Q):
            if idx + 5 > len(tok):
                return False, "short routes"
            x = int(tok[idx]); kx = int(tok[idx + 1]); m = int(tok[idx + 2]); y = int(tok[idx + 3]); ky = int(tok[idx + 4])
            idx += 5
            if not (0 <= x < S and 0 <= y < S and 0 <= m < M and 0 <= kx < K and 0 <= ky < K):
                return False, "route range"
            if x // sp != m // oxcs_per_plane or y // sp != m // oxcs_per_plane:
                return False, "plane mismatch"
            gA, _leafA, gB, _leafB = flows[i]
            portA = gA * ports_per_group + (x % sp) * K + kx
            portB = gB * ports_per_group + (y % sp) * K + ky
            if cfg[m][portA] != portB or cfg[m][portB] != portA:
                return False, "no connection"

    return True, "ok"


def main() -> int:
    rng = random.Random(0)
    exe = r"C:\Code_Turnament\main2.exe"
    for t in range(2000):
        inp = gen_case(rng)
        pathlib.Path("last_case.txt").write_text(inp, encoding="utf-8")
        p = subprocess.run([exe], input=inp.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if p.returncode != 0:
            print("RUNTIME", t, p.returncode, p.stderr[:200].decode(errors="ignore"))
            print(inp)
            return 1
        ok, msg = check_output(inp, p.stdout.decode())
        if not ok:
            print("FAIL", t, msg)
            print(inp)
            return 2
    print("stress ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

