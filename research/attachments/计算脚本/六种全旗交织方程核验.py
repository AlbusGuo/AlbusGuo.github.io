"""Check six-Borel transport against full intertwining equations."""
import json
from pathlib import Path
from 六种全旗表示模型 import ORDERS,canonical,transform_weight,transform_order,base_weight,full_model
from 六种全旗奇异向量核验 import predicted
from 特殊线性超群根基计算 import hom


def main():
    count=0;nonzero=0;double=0
    for p,r in [(3,1),(3,2)]:
        q=p**r
        weights=[(0,0),(q-1,0),(1,1),(-2*q,q)]
        cache={}
        def module(order,weight,parity,forget):
            key=(order,weight,parity,forget)
            if key not in cache:
                m=full_model(order,p,r,*weight,parity)
                if forget:m['weights']=[(a%q,b%q,e) for a,b,e in m['weights']]
                cache[key]=m
            return cache[key]
        for target_order in ORDERS:
            model,swap,reverse=canonical(target_order)
            for target_weight in weights:
                a,b=transform_weight(*target_weight,swap,reverse)
                for source_order in ORDERS:
                    order=transform_order(source_order,swap,reverse)
                    vectors=predicted(model,order,p,r,a,b)
                    primitive_weights=[base_weight(model,next(iter(v)),a,b) for v in vectors]
                    for source_weight in weights:
                        x,y=transform_weight(*source_weight,swap,reverse)
                        for parity in [0,1]:
                            for forget in [False,True]:
                                expected=sum(e==parity and
                                    ((u-x)%q==0 and (v-y)%q==0 if forget else (u,v)==(x,y))
                                    for u,v,e in primitive_weights)
                                maps=hom(module(source_order,source_weight,parity,forget),
                                         module(target_order,target_weight,0,forget),p)
                                assert len(maps)==expected,(p,r,source_order,target_order,source_weight,target_weight,parity,forget,len(maps),expected)
                                count+=1;nonzero+=bool(maps);double+=len(maps)==2
    result={'status':'passed','full_intertwining_cases':count,'nonzero_cases':nonzero,
            'two_dimensional_cases':double,'parameters':[[3,1],[3,2]],
            'scope':'All 36 flag Borel pairs, four source/target weights, both parity choices, with and without T.'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/六种全旗交织方程核验结果.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
