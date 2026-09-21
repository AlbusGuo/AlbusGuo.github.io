"""核验任意最高权的变权同态、核像及高阶终端判据。

一般G中的结论由PBW及根分次证明；本程序只核验根方向的系数。
源目标最高权向量奇偶性相反，所比较的同态本身为偶同态。
"""
from math import comb,prod
from pathlib import Path
import json
from 秩一同态核验 import osp_action,choose,compose,normalize

def shift_map(p,r,weight):
    residue=weight%p
    out=[]
    for i in range(p**r):
        j=i+residue
        out.append((2*j+1,choose(j,residue)%p) if j<p**r else (0,0))
        j=i+residue+1
        out.append((2*j,(-2*(residue+1)*choose(j,residue+1))%p) if j<p**r else (0,0))
    return out

def image(mapping,p):return {i for i,c in mapping if c%p}
def kernel(mapping,p):return {i for i,(_,c) in enumerate(mapping) if not c%p}
def expected_submodule(p,r,weight):
    residue=weight%p
    return {2*i+odd for i in range(p**r) for odd in (0,1) if i%p>=residue+1-odd}

def check(p,r,weight):
    residue=weight%p
    shifted=weight-(2*residue+1)
    first=shift_map(p,r,weight)
    second=shift_map(p,r,shifted)
    for src,(dst,coefficient) in enumerate(first):
        if coefficient%p:
            assert shifted-src==weight-dst
            assert (src+1)%2==dst%2
    assert shifted-2*(shifted%p)-1==weight-2*p
    assert image(first,p)==expected_submodule(p,r,weight)
    assert kernel(first,p)==expected_submodule(p,r,shifted)==image(second,p)
    assert all(normalize(compose(first,v),p)[1]==0 for v in second)
    # Check every positive and negative divided power, not just Lie generators.
    for op,s in [('x',1),('y',1)]+[(op,s) for op in ('E','F') for s in range(p**r)]:
        src=[osp_action(op,s,i,shifted,p,p**r) for i in range(2*p**r)]
        dst=[osp_action(op,s,i,weight,p,p**r) for i in range(2*p**r)]
        for i in range(2*p**r):
            assert normalize(compose(first,src[i]),p)==normalize(compose(dst,first[i]),p),(p,r,weight,op,s,i)
    original=[]
    for i in range(p**r):
        original.extend([(2*(p**r-1-i)+1,choose(-weight+p**r-1+i,i)%p),
                         (2*(p**r-1-i),2*weight*choose(-weight+p**r+i,i)%p)])
    actual_kernel=kernel(original,p);u=image(first,p)
    assert u<=actual_kernel
    digits=[(weight//p**j)%p for j in range(r)]
    expected=(2*residue+1)*(p**(r-1)-prod(x+1 for x in digits[1:]))
    assert len(actual_kernel-u)==expected
    assert (actual_kernel==u)==all(x==p-1 for x in digits[1:])
    # Nonzero source indices in the quotient use small low digit and failed high binomial.
    high=(weight%p**r-residue)//p
    quotient={2*(i0+p*j)+odd for j in range(p**(r-1)) if choose(high,j)%p==0
              for odd in (0,1) for i0 in range(residue+1-odd)}
    assert quotient==actual_kernel-u
    # Check the formal character identity over Z[z,zeta]/(zeta^2-1), without mod p.
    def polynomial(indices):return {(i,i%2):1 for i in indices}
    def shifted_polynomial(poly,degree,parity):return {(i+degree,(e+parity)%2):c for (i,e),c in poly.items()}
    def difference(left,right):
        result=dict(left)
        for key,value in right.items():result[key]=result.get(key,0)-value
        return {k:v for k,v in result.items() if v}
    full=polynomial(range(2*p**r));sub=polynomial(u)
    assert difference(sub,shifted_polynomial(sub,2*p,0))==difference(shifted_polynomial(full,2*residue+1,1),shifted_polynomial(full,2*p,0))
    # Every root-direction singular vector in the old kernel is in the new image.
    for idx in actual_kernel:
        singular=osp_action('x',1,idx,weight,p,p**r)[1]==0
        singular=singular and all(osp_action('E',s,idx,weight,p,p**r)[1]==0 for s in range(1,p**r))
        if singular:assert idx in u
    return {'p':p,'r':r,'最高权坐标':weight,'最低位':residue,'原核维数':len(actual_kernel),'正合列终端维数':len(u),'缺失商维数':expected,'可满射到原核':actual_kernel==u}

def main():
    records=[];count=0
    for p,rmax in [(3,3),(5,2),(7,2)]:
        for r in range(1,rmax+1):
            for weight in list(range(p**r))+[-p**r-1,-1,p**r,p**r+1]:
                rec=check(p,r,weight);count+=1
                if p==3 and r==2 and 0<=weight<9:records.append(rec)
    result={'状态':'通过','最高权参数组':count,'检查':'核像基集合、连续复合、全部同根divided powers及奇根交织、商基和终端等号条件、保奇特征标恒等式、核中奇异向量归属','范围':'p=3,r≤3；p=5或7,r≤2；全部模p^r最高权及负权/平移边界','示例':records,'边界':'有限实验不替代一般G的PBW与根分次论证，不构成原创性认证'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/变权正合列核验结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
