"""Verify odd-root ranks and explicit homology representatives."""
import json
from pathlib import Path
from 六种全旗表示模型 import full_model
from 特殊线性超群根基计算 import rref


def main():
    rows=[]
    for p,r in [(3,1),(3,2),(3,3),(5,1),(5,2)]:
        m=full_model('132',p,r,0,0);q=p**r;n=4*q;result={}
        for j,op in enumerate(['x1','x2','y1','y2']):
            action=m['actions'][2*r+j]
            images=[[col.get(i,0) for i in range(n)] for col in action]
            rank=len(rref(images,n,p)[0])
            expected=2*q-2 if op in ['x1','y2'] else 2*q
            assert rank==expected
            if op in ['x1','y2']:
                indices=[0,1,4*(q-1)+2,4*q-1] if op=='x1' else [0,2,4*(q-1)+1,4*q-1]
                assert all(not action[i] for i in indices)
                representatives=[[int(i==j) for j in range(n)] for i in indices]
                assert len(rref(images+representatives,n,p)[0])==rank+4
            result[op]={'rank':rank,'homology_dimension':n-2*rank}
        rows.append({'p':p,'r':r,'odd_roots':result,'status':'passed'})
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/中间奇根同调核验结果.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(rows))


if __name__=='__main__':main()
