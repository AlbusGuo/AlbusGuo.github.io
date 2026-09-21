"""Audit the first-kernel quotient used in the middle radical proof."""
import json
from pathlib import Path
from 六种全旗表示模型 import full_model
from 中间正根系全权根基核验 import depths
from 中间正根系整环境核验 import lift,v
from 特殊线性超群根基计算 import radical_profile,submodule,rref


def main():
    output=[]
    for p,r,a in [(3,2,3),(3,2,6),(3,3,9)]:
        full=full_model('132',p,r,a,0);n=full['dim'];q=p**r;degrees=depths(p,r,a)
        s=min(v(a,p),r);H=(a%q+2*q)//p;c=s+1+min(v(H-1,p),r-1)
        for depth in range(1,r+s):
            rows=[[int(i==j) for j in range(n)] for i,d in enumerate(degrees) if d>=depth]
            f=submodule(full,rows,p)
            restricted=dict(f,actions=[f['actions'][j] for j in [0,r,2*r,2*r+1,2*r+2,2*r+3]])
            dims,heads,bases=radical_profile(restricted,p,1,with_embeddings=True)
            kg1=[[sum(z*row[j] for z,row in zip(vector,rows))%p for j in range(n)] for vector in bases[1]]
            k=rref(kg1,n,p)[0];rank=len(k)
            def inside(vector):return len(rref(k+[vector],n,p)[0])==rank
            assert all(not z or degrees[i]>=depth+1 for row in k for i,z in enumerate(row))
            assert all(not row[4*p*j] for row in k for j in range(q//p))
            # The canonical Q,V,W,I projections must individually preserve K.
            for row in k:
                parts=[[0]*n for _ in range(4)]
                for i in range(q):
                    parts[1][4*i+2]=row[4*i+2]
                    parts[2][4*i+1]=row[4*i+1]
                    if i%p==0:parts[0][4*i]=row[4*i]
                    else:
                        x=row[4*i]*pow(i%p,-1,p)%p
                        parts[1][4*(i-1)+3]=(parts[1][4*(i-1)+3]+x)%p
                        parts[2][4*(i-1)+3]=(parts[2][4*(i-1)+3]-x)%p
                        parts[2][4*i]=row[4*i]
                    if (i+1)%p==0:parts[3][4*i+3]=row[4*i+3]
                    else:parts[1][4*i+3]=(parts[1][4*i+3]+row[4*i+3])%p
                assert all(inside(part) for part in parts)
            if depth<s:
                assert inside([int(j==2) for j in range(n)])
                assert inside([int(j==1) for j in range(n)])
            if depth<c:assert inside([int(j==4*(p-1)+3) for j in range(n)])
            output.append({'p':p,'r':r,'a':a,'depth':depth,'F_dimension':len(rows),'first_kernel_radical_dimension':rank,'status':'passed'})
            print(json.dumps(output[-1]),flush=True)
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/中间第一核专项核验结果.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
