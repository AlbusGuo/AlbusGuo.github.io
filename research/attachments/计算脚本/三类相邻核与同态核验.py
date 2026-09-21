"""三种根分开核验；同字母d的数学含义不在case间复用。

有限检查包括偶根新变权列与核的Hom空间。Ext结论由笔记中的一般证明给出。
"""
from math import prod
from pathlib import Path
import json
from 秩一同态核验 import choose,osp_action,compose,normalize
from 变权正合列核验 import shift_map

def image(mapping,p):return {j for j,c in mapping if c%p}
def kernel(mapping,p):return {i for i,(_,c) in enumerate(mapping) if not c%p}

def even_action(op,s,i,weight,p,size):
    j=i+s if op=='F' else i-s
    coefficient=choose(i+s,s) if op=='F' else choose(weight-i+s,s)
    return (j,coefficient%p) if 0<=j<size and coefficient%p else (0,0)

def even_case(p,r,weight):
    d=(-weight-1)%p**r  # Case 1: negative shifted coroot pairing, modulo p^r.
    if d==0:return {'d':0,'同构情形':True},set(),[]
    ds=[(d//p**j)%p for j in range(r)]
    nu=next(j for j,x in enumerate(ds) if x)
    exponent=(p-ds[nu])*p**nu
    first=[(i+exponent,choose(i+exponent,exponent)%p) if i+exponent<p**r else (0,0) for i in range(p**r)]
    shifted=weight-2*exponent
    next_d=(-shifted-1)%p**r
    next_ds=[(next_d//p**j)%p for j in range(r)]
    assert next_ds[nu]==p-ds[nu] and all(x==0 for x in next_ds[:nu])
    second_exp=ds[nu]*p**nu
    second=[(i+second_exp,choose(i+second_exp,second_exp)%p) if i+second_exp<p**r else (0,0) for i in range(p**r)]
    assert exponent+second_exp==p**(nu+1)
    assert kernel(first,p)==image(second,p)
    assert all(normalize(compose(first,v),p)[1]==0 for v in second)
    for i,(j,c) in enumerate(first):
        if c:assert shifted-2*i==weight-2*j
    for op in ('E','F'):
        for s in range(p**r):
            src=[even_action(op,s,i,shifted,p,p**r) for i in range(p**r)]
            dst=[even_action(op,s,i,weight,p,p**r) for i in range(p**r)]
            for i in range(p**r):assert normalize(compose(first,src[i]),p)==normalize(compose(dst,first[i]),p),(p,r,weight,op,s,i)
    original=[(p**r-1-i,choose(d+i,i)%p) for i in range(p**r)]
    ker=kernel(original,p);im=image(first,p)
    assert im<=ker
    assert im=={i for i in range(p**r) if (i//p**nu)%p>=p-ds[nu]}
    expected=p**nu*(p-ds[nu])*(p**(r-nu-1)-prod(p-x for x in ds[nu+1:]))
    assert len(ker-im)==expected
    assert (ker==im)==all(x==0 for x in ds[nu+1:])
    high=(d-ds[nu]*p**nu)//p**(nu+1)
    quotient={a+b*p**nu+j*p**(nu+1) for a in range(p**nu) for b in range(p-ds[nu])
              for j in range(p**(r-nu-1)) if choose(high+j,j)%p==0}
    assert quotient==ker-im
    actions=[[even_action(op,p**j,i,weight,p,p**r) for i in range(p**r)] for op in ('E','F') for j in range(r)]
    return {'d':d,'nu':nu,'首步指数':exponent,'核维数':len(ker),'变权像维数':len(im),'遗漏商维数':expected,'到达核':ker==im},ker,actions

def isotropic_case(p,r,weight):
    d=weight%p  # Case 2: coroot pairing, modulo p only.
    if d:return {'d':d,'同构情形':True},set(),[]
    first=[(1,1),(0,0)]
    assert kernel(first,p)==image(first,p)=={1}
    return {'d':0,'核维数':1,'变权像维数':1,'到达核':True},{1},[[(0,0),(0,0)],[(1,1),(0,0)]]

def nonisotropic_case(p,r,weight):
    d=weight%p**r  # Case 3: pairing with chi_(2alpha), modulo p^r.
    ds=[(d//p**j)%p for j in range(r)]
    first=shift_map(p,r,weight)
    original=[]
    for i in range(p**r):
        original.extend([(2*(p**r-1-i)+1,choose(-weight+p**r-1+i,i)%p),
                         (2*(p**r-1-i),2*weight*choose(-weight+p**r+i,i)%p)])
    ker=kernel(original,p);im=image(first,p)
    assert im<=ker
    expected=(2*ds[0]+1)*(p**(r-1)-prod(x+1 for x in ds[1:]))
    assert len(ker-im)==expected
    ops=[('x',1),('y',1)]+[(op,p**j) for op in ('E','F') for j in range(r)]
    actions=[[osp_action(op,s,i,weight,p,p**r) for i in range(2*p**r)] for op,s in ops]
    return {'d':d,'核维数':len(ker),'变权像维数':len(im),'遗漏商维数':expected,'到达核':ker==im},ker,actions

def hom_dimension(domain,target,actions):
    # Common labels have identical integer T weight and parity; variables are diagonal.
    common=domain&target
    parent={i:i for i in common};forced=set()
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    def union(i,j):parent[find(j)]=find(i)
    for action in actions:
        for i in domain:
            j,c=action[i]
            if not c:continue
            left=j in domain and j in common
            right=i in common and j in target
            if left and right:union(j,i)
            elif left:forced.add(j)
            elif right:forced.add(i)
    killed={find(i) for i in forced}
    return len({find(i) for i in common}-killed)

def check_homs(ker,actions):
    if not ker:return
    full=set(range(len(actions[0])));quotient=full-ker
    assert quotient and 0 in quotient
    for action in actions:
        for i in ker:
            j,c=action[i]
            assert not c or j in ker
    assert hom_dimension(ker,ker,actions)==1
    assert hom_dimension(ker,full,actions)==1
    assert hom_dimension(full,ker,actions)==0
    assert hom_dimension(ker,quotient,actions)==0
    assert hom_dimension(quotient,ker,actions)==0
    assert hom_dimension(quotient,quotient,actions)==1
    assert hom_dimension(full,quotient,actions)==1
    assert hom_dimension(quotient,full,actions)==0

def main():
    counts={};examples={}
    for name,fn in [('偶根',even_case),('各向同性奇根',isotropic_case),('非各向同性奇根',nonisotropic_case)]:
        count=0;hom_count=0;sample=[]
        for p,rmax in [(3,3),(5,2),(7,2)]:
            for r in range(1,rmax+1):
                weights=list(range(p if name=='各向同性奇根' else p**r))+[-p**r-1,-1,p**r,p**r+1]
                for weight in weights:
                    rec,ker,actions=fn(p,r,weight)
                    check_homs(ker,actions);count+=1;hom_count+=bool(ker)
                    if p==3 and r==2 and 0<=weight<9:sample.append({'最高权坐标':weight,**rec})
        counts[name]={'参数组':count,'非零核Hom检查组':hom_count};examples[name]=sample
    output={'状态':'通过','三种case分别核验':counts,'示例':examples,'证据边界':'根方向有限核验；一般G结论及Ext维数由新笔记中的证明给出，未以程序模拟全部Ext群'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/三类相邻核与同态核验结果.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps({'状态':output['状态'],'三种case分别核验':counts},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
