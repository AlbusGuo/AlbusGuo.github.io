"""Exact examples of radical/socle series in the unresolved two-zero region."""
from pathlib import Path
import json
from 特殊线性超群根基计算 import baby, radical_profile, dual_module
from 特殊线性超群环境配对核验 import val, check_family


def main():
    cases=[(3,2,a) for a in [2,5,8]]+[(3,3,a) for a in [2,5,8,11,17,26]]+[(5,2,a) for a in [4,9,24]]
    root=Path(__file__).resolve().parents[1]
    target=root/'核验数据/双零配对根基与底核验结果.json'
    records=[]
    for p,r,a in cases:
        module=baby(p,r,a,0)
        rd,rh=radical_profile(module,p,r)
        dd,dh=radical_profile(dual_module(module,p,r),p,r)
        sd=[module['dim']-x for x in dd]
        length=len(rd)-1
        record={'p':p,'r':r,'weight':[a,0],'s':min(val(a+1,p),r),
                'radical_dimensions':rd,'socle_dimensions':sd,'radical_layer_simples':rh,
                'loewy_length':length,'rigid':sd==list(reversed(rd)),
                'r_plus_s_plus_1_prediction':r+min(val(a+1,p),r)+1,
                'ambient_dimensions':check_family(p,r,a,0)['filtration_dimensions']}
        records.append(record)
        target.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in record.items() if k!='radical_layer_simples'},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
