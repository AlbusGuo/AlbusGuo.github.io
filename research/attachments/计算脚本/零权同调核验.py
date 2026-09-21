"""由两端秩一作用及自然同态求零权同调，独立核对对偶与Hom结论。

这是有限参数核验，不证明一般G的诱导归约。公式来源见
笔记库/高阶核表示论/相邻同态/核与像.md 的(O0)、(O1)，以及
笔记库/高阶核表示论/秩一表示/同态与简单模.md 的秩一作用公式。
"""
from math import comb
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def binomial(n, k):
    if k < 0:
        return 0
    if n >= 0:
        return comb(n, k) if k <= n else 0
    return (-1) ** k * comb(k - n - 1, k)

def nullspace(rows, width, p):
    rows = [[x % p for x in row] for row in rows if any(x % p for x in row)]
    pivots = []
    for col in range(width):
        found = next((i for i in range(len(pivots), len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        pos = len(pivots)
        rows[pos], rows[found] = rows[found], rows[pos]
        scale = pow(rows[pos][col], -1, p)
        rows[pos] = [(x * scale) % p for x in rows[pos]]
        for i in range(len(rows)):
            if i != pos and rows[i][col]:
                scalar = rows[i][col]
                rows[i] = [(a - scalar * b) % p for a, b in zip(rows[i], rows[pos])]
        pivots.append(col)
    basis = []
    for free in sorted(set(range(width)) - set(pivots)):
        vector = [0] * width
        vector[free] = 1
        for i, pivot in enumerate(pivots):
            vector[pivot] = -rows[i][free] % p
        basis.append(vector)
    return basis

def check(p, r):
    q, lower = p ** r, p ** (r - 1)
    mu = -(2 * q - 1)
    basis = [(kind, i) for kind in (0, 1) for i in range(q)]

    def term(kind, i, coefficient):
        coefficient %= p
        return ((kind, i), coefficient) if 0 <= i < q and coefficient else None

    def action(side, generator, v):
        kind, i = v
        name, degree = generator
        if side == 0:
            if name == 'x':return term(1, i - 1, 1) if kind == 0 else term(0, i, -2 * i)
            if name == 'y':return term(1, i, 1) if kind == 0 else term(0, i + 1, -2 * (i + 1))
            if name == 'E':return term(kind, i - degree, binomial(-kind - i + degree, degree))
            if name == 'F':return term(kind, i + degree, binomial(i + degree, degree))
        else:
            if name == 'x':return term(1, i, 1) if kind == 0 else term(0, i + 1, 2 * (i + 1))
            if name == 'y':return term(1, i - 1, 1) if kind == 0 else term(0, i, 2 * (mu + i))
            if name == 'E':return term(kind, i + degree, binomial(i + degree, degree))
            if name == 'F':return term(kind, i - degree, binomial(-mu - kind - i + degree, degree))
        raise ValueError(generator)

    def morphism(side, v):
        kind, i = v
        if side == 0:
            return term(1, q - 1 - i, binomial(q - 1 + i, i)) if kind == 0 else None
        return term(1, q - 1 - i, binomial(-q + i, i)) if kind == 0 else term(0, q - 1 - i, 2 * binomial(-q + 1 + i, i))

    def compose(f, value):
        if value is None:return None
        output = f(value[0])
        if output is None:return None
        coefficient = value[1] * output[1] % p
        return (output[0], coefficient) if coefficient else None

    generators = [('x', 1), ('y', 1)] + [(name, p ** a) for name in ('E', 'F') for a in range(r)]
    for side in (0, 1):
        for v in basis:
            assert compose(lambda w: morphism(1 - side, w), morphism(side, v)) is None
            for g in generators:
                assert compose(lambda w: morphism(side, w), action(side, g, v)) == compose(lambda w: action(1 - side, g, w), morphism(side, v)), (p, r, side, g, v)

    kernels = [{v for v in basis if morphism(side, v) is None} for side in (0, 1)]
    images = [{morphism(1 - side, v)[0] for v in basis if morphism(1 - side, v)} for side in (0, 1)]
    cohom = [sorted(kernels[side] - images[side]) for side in (0, 1)]
    assert cohom[0] == [(0, p * j) for j in range(1, lower)]
    assert cohom[1] == [(1, p * j - 1) for j in range(1, lower)]

    def quotient_action(side, g):
        positions = {v: i for i, v in enumerate(cohom[side])}
        matrix = []
        for v in cohom[side]:
            result = action(side, g, v)
            assert result is None or result[0] in kernels[side]
            matrix.append({positions[result[0]]: result[1]} if result and result[0] not in images[side] else {})
        return matrix

    n = lower - 1
    # In the displayed H1 basis, duality matches the same j; the twist is -2q.
    for j in range(1, lower):
        assert mu + 2 * (p * j - 1) + 1 == -2 * q - (-2 * p * j)
    for name in ('x', 'y', 'E', 'F'):
        degrees = [1] if name in ('x', 'y') else range(q)
        for s in degrees:
            left, right = [quotient_action(side, (name, s)) for side in (0, 1)]
            dual = [{} for _ in range(n)]
            sign = -1 if name in ('x', 'y') else (-1) ** s
            for i, outputs in enumerate(left):
                for j, value in outputs.items():dual[j][i] = sign * value % p
            assert dual == right, (p, r, 'dual', name, s)

    def hom(source, target):
        weights = [[-2 * p * j for j in range(1, lower)], [-2 * q + 2 * p * j for j in range(1, lower)]]
        target_index = {weight: i for i, weight in enumerate(weights[target])}
        match = [target_index[weight] for weight in weights[source]]
        inverse = {j: i for i, j in enumerate(match)}
        equations = []
        for g in generators:
            source_action, target_action = quotient_action(source, g), quotient_action(target, g)
            for i in range(n):
                rows = {}
                for j, value in source_action[i].items():
                    rows.setdefault(match[j], [0] * n)[j] += value
                for j, value in target_action[match[i]].items():
                    rows.setdefault(j, [0] * n)[i] -= value
                equations.extend(rows.values())
        return nullspace(equations, n, p), match

    if r == 1:
        return {'p': p, 'r': r, '同调维数': 0, '两端同调为零': True}
    end0, _ = hom(0, 0);end1, _ = hom(1, 1)
    forward, match = hom(0, 1);backward, backmatch = hom(1, 0)
    assert len(end0) == len(end1) == len(forward) == len(backward) == 1
    rank01 = sum(value != 0 for value in forward[0]);rank10 = sum(value != 0 for value in backward[0])
    assert rank01 == p - 1
    assert rank10 == (p - 1) * p ** (r - 2)
    composition = [forward[0][i] * backward[0][match[i]] % p for i in range(n)]
    if r == 2:assert rank01 == rank10 == n and len(set(composition)) == 1 and composition[0]
    else:assert not any(composition)
    return {'p': p, 'r': r, '同调维数': n, '对偶同构核验': True, '两端自同态维数': [len(end0), len(end1)], '相互同态维数': [len(forward), len(backward)], '相互同态的秩': [rank01, rank10], '同构': r == 2, '两向复合为零': r > 2}

def main():
    cases = [(3, 1), (3, 2), (3, 3), (3, 4), (5, 1), (5, 2), (5, 3), (7, 1), (7, 2), (7, 3)]
    results = [check(p, r) for p, r in cases]
    report = {'性质': '有限计算核验；一般证明见正文', '范畴': '保留整数T权及奇性的秩一模', '案例': results}
    target = ROOT/'核验数据/零权同调核验结果.json'
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':main()
