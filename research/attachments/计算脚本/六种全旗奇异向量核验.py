"""Positive kernels for both target models and every flag source Borel."""
from pathlib import Path
import json
from 六种全旗表示模型 import action,base_weight,positive,ORDERS,ROOT_WEIGHT
from 标准正根系同态核验 import predictions,primitive
from 特殊线性超群根基计算 import rref
from 秩一同态核验 import height,choose


def predicted(model,order,p,r,a,b):
    q=p**r;N=q-1;out=[]
    def add(v):
        v={i:c%p for i,c in v.items() if c%p}
        assert v
        out.append(v)
    if model=='123':
        if order=='123':return [row['vector'] for row in predictions(p,r,a,b)]
        if order=='132':
            for i in range(q):
                if primitive(a,i,p):add({4*i+2:1})
                if (i==0 and (a+b+1)%p==0) or (i>0 and b%p==0 and primitive(a,i,p)):
                    add({4*i+3:1})
        elif order=='213':
            add({4*N:1})
            if (a+b+1)%p==0:add({4*N+1:1})
            if b%p==0:
                add({4*N+2:1,4*(N-1)+1:-1})
                if (a+2)%p==0:add({4*N+3:1})
        elif order=='231':
            add({4*N+1:1})
            if b%p==0:add({4*N+3:1})
        elif order=='312':
            for i in range(q):
                if primitive(a,i,p):add({4*i+3:1})
        else:add({4*N+3:1})
    else:
        if order=='123':
            for i in range(q):
                if primitive(a-1,i,p):add({4*i+2:1})
                if (a+b)%p==0 and primitive(a-2,i,p):
                    add({4*i+3:1,**({4*(i+1):-(i+1)} if i+1<q else {})})
        elif order=='132':
            add({0:1})
            if (a+b)%p==0:add({1:1})
            if b%p==0:add({2:1})
            if b%p==0:
                for j in range(1,q+1):
                    if (a-j)%p**max(1,height(j-1,p))==0:add({4*(j-1)+3:1})
            else:
                for j in range(1,q):
                    if primitive(a-1,j,p):add({4*(j-1)+3:1,4*j:b})
        elif order=='213':
            add({4*N+2:1})
            if (a+b)%p==0:add({4*N+3:1})
        elif order=='231':add({4*N+3:1})
        elif order=='312':
            for i in range(q):
                if primitive(a-1,i,p):add({4*i+1:1})
                if b%p==0 and primitive(a-2,i,p):add({4*i+3:1})
        elif order=='321':
            add({4*N+1:1})
            if b%p==0:add({4*N+3:1})
    return out


def apply_op(model,op,s,vector,p,r,a,b):
    result={}
    for i,c in vector.items():
        for j,v in action(model,op,s,i,a,b,p,r).items():result[j]=(result.get(j,0)+c*v)%p
    return {i:c for i,c in result.items() if c}


def relation_checks(p,r,a,b):
    model='132';q=p**r
    relations=[('E','F',0,{'h1':1}),('x1','y1',1,{'h1':1,'h2':1}),
               ('x2','y2',1,{'h2':1}),('x1','y2',1,{'E':1}),('x2','y1',1,{'F':1}),
               ('x1','x2',1,{}),('y1','y2',1,{})]
    for x,y,odd,target in relations:
        for i in range(4*q):
            lhs=apply_op(model,x,1,action(model,y,1,i,a,b,p,r),p,r,a,b)
            second=apply_op(model,y,1,action(model,x,1,i,a,b,p,r),p,r,a,b)
            for j,c in second.items():lhs[j]=(lhs.get(j,0)-(-1)**odd*c)%p
            rhs={}
            for z,c in target.items():
                if z in ['h1','h2']:
                    value=base_weight(model,i,a,b)[0 if z=='h1' else 1]
                    rhs[i]=(rhs.get(i,0)+c*value)%p
                else:
                    for j,v in action(model,z,1,i,a,b,p,r).items():rhs[j]=(rhs.get(j,0)+c*v)%p
            assert {j:c for j,c in lhs.items() if c}=={j:c for j,c in rhs.items() if c},(p,r,a,b,x,y,i)
    for x in ['x1','x2','y1','y2']:
        for i in range(4*q):assert not apply_op(model,x,1,action(model,x,1,i,a,b,p,r),p,r,a,b)
    # Divided powers also have to interact correctly with the odd roots.
    cross={('E','y1'):('y2',-1),('E','x2'):('x1',1),
           ('F','x1'):('x2',1),('F','y2'):('y1',-1)}
    for even in ['E','F']:
        for odd in ['x1','x2','y1','y2']:
            for h in range(1,q):
                for i in range(4*q):
                    lhs=apply_op(model,even,h,action(model,odd,1,i,a,b,p,r),p,r,a,b)
                    second=apply_op(model,odd,1,action(model,even,h,i,a,b,p,r),p,r,a,b)
                    for j,c in second.items():lhs[j]=(lhs.get(j,0)-c)%p
                    rhs={}
                    if (even,odd) in cross:
                        z,c=cross[even,odd]
                        rhs={j:c*v%p for j,v in apply_op(model,z,1,action(model,even,h-1,i,a,b,p,r),p,r,a,b).items()}
                    assert {j:c for j,c in lhs.items() if c}==rhs,('odd-divided',p,r,a,b,even,odd,h,i)
    # Check the full divided-power sl2 commutation relation, not only E,F.
    for s in range(q):
        for t in range(q):
            for i in range(4*q):
                lhs=apply_op(model,'E',s,action(model,'F',t,i,a,b,p,r),p,r,a,b)
                rhs={}
                h=base_weight(model,i,a,b)[0]
                for j in range(min(s,t)+1):
                    c=choose(h+s-t,j)%p
                    if not c:continue
                    term=apply_op(model,'F',t-j,action(model,'E',s-j,i,a,b,p,r),p,r,a,b)
                    for k,v in term.items():rhs[k]=(rhs.get(k,0)+c*v)%p
                assert lhs=={j:c for j,c in rhs.items() if c},('divided',p,r,a,b,s,t,i)
                for op in ['E','F']:
                    lhs=apply_op(model,op,s,action(model,op,t,i,a,b,p,r),p,r,a,b)
                    c=choose(s+t,s)%p
                    rhs={j:c*v%p for j,v in action(model,op,s+t,i,a,b,p,r).items() if c*v%p} if s+t<q else {}
                    assert lhs==rhs,('same-divided',p,r,a,b,op,s,t,i)


def kernel_check(model,order,p,r,a,b):
    q=p**r
    groups={}
    for i in range(4*q):groups.setdefault(base_weight(model,i,a,b),[]).append(i)
    expected={}
    for v in predicted(model,order,p,r,a,b):
        w=base_weight(model,next(iter(v)),a,b)
        assert all(base_weight(model,i,a,b)==w for i in v)
        assert w not in expected
        expected[w]=v
    residues={}
    for w,indices in groups.items():
        eq=[]
        for op,s in positive(order,r,p):
            block={}
            for col,i in enumerate(indices):
                for j,c in action(model,op,s,i,a,b,p,r).items():block.setdefault(j,[0]*len(indices))[col]=c
            eq.extend(block.values())
        rr,pivots=rref(eq,len(indices),p)
        dimension=len(indices)-len(pivots)
        assert dimension==int(w in expected),(model,order,p,r,a,b,w,dimension)
        if dimension:
            vector=expected[w]
            coords=[vector.get(i,0) for i in indices]
            assert all(sum(c*x for c,x in zip(row,coords))%p==0 for row in eq)
            key=(w[0]%q,w[1]%q,w[2])
            residues[key]=residues.get(key,0)+1
    maximum=max(residues.values(),default=0)
    assert maximum<=(2 if model==order=='132' and a%q==0 and b%p==0 else 1)
    if model==order=='132' and a%q==0 and b%p==0:assert residues[a%q,b%q,0]==2
    return len(expected),maximum


def main():
    for p,r in [(3,1),(3,2),(5,1)]:
        for a in range(p**r):
            for b in range(p):relation_checks(p,r,a,b)
    count=0;max_forget=0;vectors=0
    for p,r in [(3,1),(3,2),(3,3),(5,1),(5,2),(7,1)]:
        for a in range(p**r):
            for b in range(p):
                for model in ['123','132']:
                    for order in ORDERS:
                        n,m=kernel_check(model,order,p,r,a,b)
                        count+=1;vectors+=n;max_forget=max(max_forget,m)
    result={'status':'passed','two_model_source_target_cases':count,'primitive_vectors':vectors,
            'middle_relations':'odd brackets and squares; all E^(s)F^(t), same-root products and odd/divided commutators in the tested range',
            'max_hom_with_T':1,'max_hom_without_T':max_forget,
            'exception':'Same middle Borel, a divisible by p^r and b divisible by p; matching source character and parity.'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/六种全旗奇异向量核验结果.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
