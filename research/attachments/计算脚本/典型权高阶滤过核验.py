"""核验Steinberg张量分解的秩一交织及一般线性超群的带奇性特征标。

一般秩的滤过存在性与和公式依据汇报笔记的证明和经典一阶定理；
本程序不声称以有限计算证明一般秩的Jantzen定理。
"""
from collections import Counter
from math import comb
from pathlib import Path
import json


def choose(n, k):
    if k < 0:
        return 0
    if n < 0:
        return (-1)**k * comb(k-n-1, k)
    return comb(n,k) if k <= n else 0


def sl2_check(p, r, mu):
    # i=a+p^(r-1)b：v_i 对应低阶Steinberg基 a 与一阶baby基 b。
    low=p**(r-1)
    weight=low-1+low*mu
    for i in range(p**r):
        a,b=i%low,i//low
        assert weight-2*i == low-1-2*a+low*(mu-2*b)
        for s in range(p**r):
            target_f = i+s
            direct_f = choose(i+s,s)%p if target_f<p**r else 0
            target_e = i-s
            direct_e = choose(weight-i+s,s)%p if target_e>=0 else 0
            tf=Counter();te=Counter()
            for j in range(s+1):
                if (s-j)%low:
                    continue
                upper=(s-j)//low
                if a+j<low and b+upper<p:
                    tf[(a+j)+low*(b+upper)] += choose(a+j,j)*choose(b+upper,upper)
                if a>=j and b>=upper:
                    te[(a-j)+low*(b-upper)] += choose(low-1-a+j,j)*choose(mu-b+upper,upper)
            tf={i:c%p for i,c in tf.items() if c%p}
            te={i:c%p for i,c in te.items() if c%p}
            assert tf == ({target_f:direct_f} if direct_f else {}),(p,r,mu,i,s,'F')
            assert te == ({target_e:direct_e} if direct_e else {}),(p,r,mu,i,s,'E')


def roots(m,n):
    size=m+n
    def root(i,j):
        a=[0]*size;a[i]=1;a[j]=-1
        return tuple(a)
    even=[root(i,j) for start,stop in ((0,m),(m,m+n)) for i in range(start,stop) for j in range(i+1,stop)]
    odd=[root(i,m+j) for i in range(m) for j in range(n)]
    return even,odd


def add_weight(a,b):
    return tuple(x+y for x,y in zip(a,b))


def multiply(a,b):
    out=Counter()
    for (wa,pa),ca in a.items():
        for (wb,pb),cb in b.items():
            out[(add_weight(wa,wb),(pa+pb)%2)]+=ca*cb
    return +out


def pbw_character(weight,even,odd,size,scale=1):
    out=Counter({(weight,0):1})
    zero=(0,)*len(weight)
    for root in even:
        out=multiply(out,Counter({(tuple(-scale*i*x for x in root),0):1 for i in range(size)}))
    for root in odd:
        out=multiply(out,Counter({(zero,0):1,(tuple(-x for x in root),1):1}))
    return out


def main():
    count=0
    for p,r in ((3,2),(3,3),(5,2)):
        for mu in range(-2,p+2):
            sl2_check(p,r,mu);count+=1
    character_checks=[]
    for m,n,p,r in ((2,2,3,2),(3,1,3,2),(2,1,5,2),(1,2,3,3)):
        even,odd=roots(m,n)
        low=p**(r-1)
        # a=n,b=0：典型因子恒为1 (mod p)。
        sigma=tuple((low-1)*(m-1-i)+n for i in range(m))+tuple((low-1)*(n-1-j) for j in range(n))
        mu=tuple((i%3)-1 for i in range(m+n))
        weight=tuple(x+low*y for x,y in zip(sigma,mu))
        typical=[(weight[i]+weight[m+j]+m-i-j-1)%p for i in range(m) for j in range(n)]
        assert set(typical)=={1}
        direct=pbw_character(weight,even,odd,p**r)
        lower=pbw_character(sigma,even,odd,low)
        upper=pbw_character(tuple(low*x for x in mu),even,[],p,low)
        assert direct==multiply(lower,upper)
        character_checks.append({'m':m,'n':n,'p':p,'r':r,'维数':sum(direct.values()),'带奇性权空间数':len(direct),'典型因子':typical})
    # GL(2|2),p=3,r=2,mu=0：两份秩一一阶滤过的卷积。
    m=n=2;p=3;r=2;low=3
    even,odd=roots(m,n);sigma=(4,2,2,0)
    lower=pbw_character(sigma,even,odd,low)
    layers=[Counter(),Counter(),Counter()]
    for i in range(p):
        for j in range(p):
            w=tuple(-low*(i*even[0][a]+j*even[1][a]) for a in range(4))
            depth=(i>0)+(j>0)
            for k in range(depth+1):layers[k][(w,0)]+=1
    layers=[multiply(lower,x) for x in layers]
    assert [sum(x.values()) for x in layers]==[1296,1152,576]
    # 以逐权比较核验无限和式：只需枚举有可能回到有限支撑的平移。
    right=Counter()
    for root in even:
        for k in range(4):
            pos=tuple(sigma[a]-low*(k*p+1)*root[a] for a in range(4))
            neg=tuple(sigma[a]-low*((k+1)*p)*root[a] for a in range(4))
            right.update(pbw_character(pos,even,odd,p**r))
            for key,c in pbw_character(neg,even,odd,p**r).items():right[key]-=c
    left=layers[1]+layers[2]
    support=set(layers[0])
    assert {w:right[w] for w in support if right[w]} == dict(left)
    # 清分母后核验整个有限Laurent多项式，而不限于原模权支撑。
    def shift(poly,vector):
        return Counter({(add_weight(w,vector),parity):c for (w,parity),c in poly.items()})
    def subtract(a,b):
        out=a.copy()
        for key,c in b.items():out[key]-=c
        return Counter({key:c for key,c in out.items() if c})
    def denominator(poly,root):
        return subtract(poly,shift(poly,tuple(-p**r*x for x in root)))
    lhs=denominator(denominator(left,even[0]),even[1])
    rhs=Counter()
    for j,root in enumerate(even):
        term=subtract(shift(layers[0],tuple(-low*x for x in root)),
                      shift(layers[0],tuple(-p**r*x for x in root)))
        rhs.update(denominator(term,even[1-j]))
    rhs=Counter({key:c for key,c in rhs.items() if c})
    assert lhs==rhs
    result={'状态':'通过','SL2全部同根divided-power交织参数组':count,
            '一般线性超群带奇性特征标':character_checks,
            'GL(2;2)示例':{'p':3,'r':2,'最高权':[4,2,2,0],'滤过层维数':[1296,1152,576,0],
                           '逐层商维数':[144,576,576],'和公式左端维数':1728,
                           '和式核验':'在完整baby Verma权支撑上逐项核验，并在清分母后核验全部Laurent多项式系数；一般秩结论依据正文证明'} }
    path=Path(__file__).resolve().parents[1]/'核验数据/典型权高阶滤过核验结果.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
