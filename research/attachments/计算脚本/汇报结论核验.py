"""汇报的有限核验：直接二项式系数计数、尖锐下界及第12.2节反例。

不以有限枚举代替汇报稿中的一般证明。输出仅写入项目。
"""
from math import comb, prod
from pathlib import Path
import json

def binomial(n,i):
    if i<0:return 0
    if n<0:return (-1)**i*comb(i-n-1,i)
    return comb(n,i) if i<=n else 0

def main():
    count=0;examples=[]
    for p,rmax in [(3,5),(5,3),(7,3),(11,2)]:
        for r in range(1,rmax+1):
            for d in range(p**r):
                ds=[(d//p**j)%p for j in range(r)]
                forward=sum(binomial(-d+p**r-1+i,i)%p!=0 for i in range(p**r))
                forward+=sum(2*d*binomial(-d+p**r+i,i)%p!=0 for i in range(p**r))
                backward=sum(binomial(d-p**r+i,i)%p!=0 for i in range(p**r))
                backward+=sum(2*(d+1)*binomial(d-p**r+1+i,i)%p!=0 for i in range(p**r))
                assert forward==(2*ds[0]+1)*prod(x+1 for x in ds[1:])
                assert backward==(2*p-2*ds[0]-1)*prod(p-x for x in ds[1:])
                defect=2*p**r-forward-backward
                assert defect>=p**(r-1)-1
                if r>1:assert (defect==p**(r-1)-1)==(d in (0,p**r-1))
                else:assert defect==0
                count+=1
                if p==3 and r==2:examples.append({'d':d,'正向秩':forward,'反向秩':backward,'两端各自同调维数':defect})
    # In SL2 at highest weight zero, E v_2 = binom(-1,1)v_1, hence v_2 is not singular.
    hom_example=[{'p':p,'E作用系数':binomial(-1,1)%p,'目标权空间维数':1,'偶Hom维数':0} for p in (3,5,7,11)]
    assert all(row['E作用系数'] for row in hom_example)
    data={'状态':'通过','非各向同性奇根参数组':count,'范围':'p=3,r≤5；p=5或7,r≤3；p=11,r≤2；每个d均枚举','下界':'p^(r-1)-1','等号条件':'r>1时恰为d=0或p^r-1','p3r2完整表':examples,'第12章反例':hom_example,'证据边界':'有限系数核验，不验证一般超群存在性，也不替代一般证明或文献查重'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/汇报结论核验.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
