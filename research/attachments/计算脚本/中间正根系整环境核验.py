"""Finite integral middle-Borel lattice and contravariant pairing checks."""
import json
from pathlib import Path
from 六种全旗表示模型 import middle_action
from 秩一同态核验 import choose


def basis(A):
    return [(i,e) for i in range(A) for e in range(4) if (i,e)!=(A-1,3)]+[(A,0)]


def finite_action(op,h,item,A,B):
    out={}
    for index,c in middle_action(op,h,4*item[0]+item[1],A,B,A+1).items():
        i,e=divmod(index,4)
        if (i,e)==(A-1,3):i,e,c=A,0,-B*c
        if i>A or (i==A and e):continue
        key=(i,e);out[key]=out.get(key,0)+c
    return {i:c for i,c in out.items() if c}


def gram(x,y,A,B):
    i,e=x;j,f=y
    if x==y:
        if e==0:return choose(A,i)
        if e==1:return (A+B)*choose(A-1,i)
        if e==2:return B*choose(A-1,i)
        return B*(A+B-i-1)*choose(A-1,i)
    if e==0 and f==3 and i==j+1:return -B*choose(A-1,j)
    if f==0 and e==3 and j==i+1:return -B*choose(A-1,i)
    return 0


def v(n,p):
    if not n:return 10**6
    out=0
    while n%p==0:n//=p;out+=1
    return out


def lift(p,r,a,b):
    q=p**r;d=a%q;e=b%q;A=d+2*q
    for t in range(1,2*p+1):
        B=e+t*q
        if v(B,p)==min(v(e,p),r) and v(A+B,p)==min(v(d+e,p),r):return A,B
    raise AssertionError((p,r,a,b))


def check_integral(A,B):
    items=basis(A);keys=set(items)
    theta={'E':'F','F':'E','x1':'y1','y1':'x1','x2':'y2','y2':'x2'}
    for op in theta:
        for h in (range(1,A+1) if op in ['E','F'] else [1]):
            actions={x:finite_action(op,h,x,A,B) for x in items}
            dual={x:finite_action(theta[op],h,x,A,B) for x in items}
            assert all(set(image)<=keys for image in actions.values())
            for x in items:
                for y in items:
                    left=sum(c*gram(z,y,A,B) for z,c in actions[x].items())
                    right=sum(c*gram(x,z,A,B) for z,c in dual[y].items())
                    assert left==right,(A,B,op,h,x,y,left,right)


def check_modular(p,r,a,b):
    q=p**r;A,B=lift(p,r,a,b);s=min(v(a,p),r);u=min(v(b,p),r);w=min(v(a+b,p),r)
    items={(i,e) for i in range(q) for e in range(4)}
    assert A>q and v(choose(A-1,q),p)==0
    for item in items:
        for op in ['E','F','x1','x2','y1','y2']:
            for h in ([p**j for j in range(r)] if op in ['E','F'] else [1]):
                assert all(z in items or c%p==0 for z,c in finite_action(op,h,item,A,B).items())
    exponents=[0]
    for i in range(q):
        eta=v(choose(A-1,i),p)
        exponents += [u+eta,w+eta]
    for i in range(1,q):
        aa=gram((i,0),(i,0),A,B);bb=gram((i,0),(i-1,3),A,B);cc=gram((i-1,3),(i-1,3),A,B)
        det=aa*cc-bb*bb
        eta0=v(choose(A-1,i-1),p);eta1=v(choose(A-1,i),p)
        small=min(v(aa,p),v(bb,p),v(cc,p));large=v(det,p)-small
        expected=eta0+min(s-v(i,p),u)
        assert small==expected and large==u+w+eta0+eta1-small
        exponents += [small,large]
    # The final D_(q-1) has its A_q partner OUTSIDE the baby module.
    aa=gram((q,0),(q,0),A,B);bb=gram((q,0),(q-1,3),A,B);cc=gram((q-1,3),(q-1,3),A,B)
    boundary=v(aa*cc-bb*bb,p)-v(aa,p) if v(bb,p)>v(aa,p) else min(v(bb,p),v(cc,p))
    assert boundary==r-s+u+w
    exponents.append(boundary)
    assert len(exponents)==4*q and max(exponents)==r-s+u+w
    return 1


def main():
    for A,B in [(3,2),(4,-1),(5,3),(6,6)]:check_integral(A,B)
    count=0
    for p,r in [(3,1),(3,2),(3,3),(5,1),(5,2)]:
        for a in range(p**r):
            for b in range(p**r):count+=check_modular(p,r,a,b)
    result={'status':'passed','integral_lattices':4,'modular_weights':count,
            'scope':'All integral divided-power contravariance in four lattices; modular baby embedding, Smith indices, external boundary and length for all weights in five parameter ranges.'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/中间整环境核验结果.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
