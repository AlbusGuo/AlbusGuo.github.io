"""Finite checks, not proofs. Run with Python -B; all output stays in project."""
from math import comb, prod
from pathlib import Path
import json


def choose(n, k):
    if k < 0:
        return 0
    if n < 0:
        return (-1) ** k * comb(k - n - 1, k)
    return comb(n, k) if k <= n else 0


def digits(n, p, r):
    return [(n // p**j) % p for j in range(r)]


def height(n, p):
    h = 0
    while p**h <= n:
        h += 1
    return h


def osp_action(op, s, idx, l, p, q, opposite=False):
    i, odd = divmod(idx, 2)
    if not opposite:
        if op == 'x':
            j, b, c = (i, 0, 2*(l-i)) if odd else (i-1, 1, 1)
        elif op == 'y':
            j, b, c = (i+1, 0, -2*(i+1)) if odd else (i, 1, 1)
        elif op == 'E':
            j, b, c = i-s, odd, choose(l-odd-i+s, s)
        elif op == 'F':
            j, b, c = i+s, odd, choose(i+s, s)
    else:
        if op == 'y':
            j, b, c = (i, 0, 2*(l+i)) if odd else (i-1, 1, 1)
        elif op == 'x':
            j, b, c = (i+1, 0, 2*(i+1)) if odd else (i, 1, 1)
        elif op == 'F':
            j, b, c = i-s, odd, choose(-l-odd-i+s, s)
        elif op == 'E':
            j, b, c = i+s, odd, choose(i+s, s)
    return (2*j+b, c % p) if 0 <= j < q and c % p else (0, 0)


def compose(a, b):
    """Apply monomial map a after a single image b."""
    idx, c = b
    if not c:
        return (0, 0)
    j, d = a[idx]
    return (j, c*d) if d else (0, 0)


def normalize(v, p):
    i, c = v
    return (i, c % p) if c % p else (0, 0)


def check_osp_maps(p, r, l):
    q = p**r
    mu = l-(2*q-1)
    phi, psi = [], []
    for i in range(q):
        phi.extend([(2*(q-1-i)+1, choose(-l+q-1+i, i) % p),
                    (2*(q-1-i), 2*l*choose(-l+q+i, i) % p)])
        psi.extend([(2*(q-1-i)+1, choose(l-q+i, i) % p),
                    (2*(q-1-i), 2*(l+1)*choose(l-q+1+i, i) % p)])
    for reverse, mapping in [(False, phi), (True, psi)]:
        src_l, dst_l = (mu, l) if reverse else (l, mu)
        operators = [('x', 1), ('y', 1)] + [(op, p**j) for op in ['E','F'] for j in range(r)]
        for op, s in operators:
            src = [osp_action(op,s,i,src_l,p,q,reverse) for i in range(2*q)]
            dst = [osp_action(op,s,i,dst_l,p,q,not reverse) for i in range(2*q)]
            for i in range(2*q):
                assert normalize(compose(mapping,src[i]),p) == normalize(compose(dst,mapping[i]),p), (p,r,l,reverse,op,s,i)
    assert all(normalize(compose(psi,v),p)[1] == 0 for v in phi)
    assert all(normalize(compose(phi,v),p)[1] == 0 for v in psi)


def main():
    counts = {'even_digit_cases':0, 'osp_digit_cases':0, 'sl2_singular_cases':0,
              'osp_singular_cases':0, 'osp_intertwiner_module_cases':0,
              'zero_weight_loewy_cases':0}
    examples=[]
    for p, max_r in [(3,4),(5,3),(7,2)]:
        for r in range(1,max_r+1):
            q=p**r
            for d in range(q):
                ds=digits(d,p,r)
                a=sum(choose(d+i,i)%p != 0 for i in range(q))
                b=sum(choose(-d+i,i)%p != 0 for i in range(q))
                assert a==prod(p-x for x in ds)
                if d:
                    nu=next(j for j,x in enumerate(ds) if x)
                    assert b==p**nu*ds[nu]*prod(x+1 for x in ds[nu+1:])
                    assert (a+b==q)==(nu==r-1)
                    for i in range(q):
                        assert choose(d+i,i)*choose(-d+q-1-i,q-1-i)%p==0
                else:
                    assert a==b==q
                counts['even_digit_cases']+=1
                osp_a=sum(choose(d,i)%p != 0 for i in range(q))+sum(2*d*choose(d-1,i)%p != 0 for i in range(q))
                osp_b=sum(choose(d+i,i)%p != 0 for i in range(q))+sum(2*(d+1)*choose(d+1+i,i)%p != 0 for i in range(q))
                assert osp_a==(2*ds[0]+1)*prod(x+1 for x in ds[1:])
                assert osp_b==(2*p-2*ds[0]-1)*prod(p-x for x in ds[1:])
                assert (osp_a+osp_b==2*q)==(r==1)
                counts['osp_digit_cases']+=1
                if (p,r,d) in [(3,2,0),(3,2,1),(3,2,3),(5,2,0)]:
                    examples.append({'p':p,'r':r,'d':d,'even_ranks':[a,b],
                                     'even_defect':q-a-b if d else None,
                                     'osp_ranks':[osp_a,osp_b],'osp_defect':2*q-osp_a-osp_b})
            # Check singularity against EVERY positive even divided power, not just Lie generators.
            for mu in range(q):
                for n in range(q):
                    actual=all(choose(mu-n+s,s)%p==0 for s in range(1,n+1))
                    expected=n==0 or (mu-n+1)%p**height(n,p)==0
                    assert actual==expected, (p,r,mu,n)
                    counts['sl2_singular_cases']+=1
                    actual_odd=(mu-n)%p==0 and all(choose(mu-1-n+s,s)%p==0 for s in range(1,n+1))
                    expected_odd=(mu-n)%p**max(1,height(n,p))==0
                    assert actual_odd==expected_odd, (p,r,mu,n)
                    counts['osp_singular_cases']+=1
            if q<=49:
                for l in range(q):
                    check_osp_maps(p,r,l)
                    counts['osp_intertwiner_module_cases']+=1
            for super_case in [False,True]:
                size=2*q if super_case else q
                ops=[(op,p**j) for op in ['E','F'] for j in range(r)]
                if super_case:
                    ops += [('x',1),('y',1)]
                graph=[set() for _ in range(size)]
                for idx in range(size):
                    for op,s in ops:
                        if super_case:
                            target,c=osp_action(op,s,idx,0,p,q)
                        elif op=='F':
                            target,c=idx+s,choose(idx+s,s)%p
                        else:
                            target,c=idx-s,choose(-idx+s,s)%p
                        if 0<=target<size and c:
                            graph[idx].add(target)
                def layer(idx):
                    i,b=divmod(idx,2) if super_case else (idx,0)
                    if b:
                        return 1
                    if not i:
                        return r+1
                    return next(j+1 for j in range(r) if i%p**(j+1))
                for idx in range(size):
                    visited={idx}
                    queue=[idx]
                    while queue:
                        v=queue.pop()
                        for w in graph[v]-visited:
                            visited.add(w)
                            queue.append(w)
                    expected={j for j in range(size) if layer(j)<=layer(idx)}
                    assert visited==expected,(p,r,super_case,idx)
                counts['zero_weight_loewy_cases']+=1
    output={'status':'passed','scope':'Finite checks only; see proof files for general arguments.',
            'counts':counts,'examples':examples}
    target=Path(__file__).resolve().parents[1]/'核验数据'/'秩一同态核验结果.json'
    target.write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(output,ensure_ascii=False))


if __name__=='__main__':
    main()
