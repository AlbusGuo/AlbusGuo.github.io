"""在F_3[c]中符号核验详解里的三维SL2扩张；只用Python标准库。"""
from pathlib import Path
import json

def poly(x):return x if isinstance(x,dict) else ({0:x%3} if x%3 else {})
def add(*args):
    out={}
    for a in args:
        for n,c in poly(a).items():out[n]=(out.get(n,0)+c)%3
    return {n:c for n,c in out.items() if c}
def scale(a,c):return {n:c*v%3 for n,v in poly(a).items() if c*v%3}
def mul(a,b):
    out={}
    for n,x in poly(a).items():
        for m,y in poly(b).items():out[n+m]=(out.get(n+m,0)+x*y)%3
    return {n:c for n,c in out.items() if c}
def matrix(rows):return [[poly(x) for x in row] for row in rows]
def mmul(a,b):return [[add(*(mul(a[i][j],b[j][k]) for j in range(3))) for k in range(3)] for i in range(3)]
def mscale(a,c):return [[scale(x,c) for x in row] for row in a]
def madd(*args):return [[add(*(a[i][j] for a in args)) for j in range(3)] for i in range(3)]
def power(a,n):
    out=matrix([[1,0,0],[0,1,0],[0,0,1]])
    for _ in range(n):out=mmul(out,a)
    return out
def zero(a):return all(not x for row in a for x in row)

def main():
    c={1:1}
    positive=matrix([[0,0,0],[0,0,2],[0,0,0]])
    negative=matrix([[0,0,0],[c,0,0],[0,2,0]])
    cartan=matrix([[0,0,0],[0,1,0],[0,0,2]])
    original_negative=matrix([[0,0,0],[1,0,0],[0,2,0]])
    lift=matrix([[1,0,0],[0,c,0],[0,0,c]])
    equations={
        '[X_alpha,X_-alpha]=H_alpha':madd(mmul(positive,negative),mscale(mmul(negative,positive),-1),mscale(cartan,-1)),
        '[H_alpha,X_alpha]=2X_alpha':madd(mmul(cartan,positive),mscale(mmul(positive,cartan),-1),mscale(positive,-2)),
        '[H_alpha,X_-alpha]=-2X_-alpha':madd(mmul(cartan,negative),mscale(mmul(negative,cartan),-1),mscale(negative,2)),
        'X_alpha^3=0':power(positive,3),
        'X_-alpha^3=0':power(negative,3),
        'H_alpha^3=H_alpha':madd(power(cartan,3),mscale(cartan,-1)),
        '正根与提升交换':madd(mmul(positive,lift),mscale(mmul(lift,positive),-1)),
        '负根与提升交织':madd(mmul(negative,lift),mscale(mmul(lift,original_negative),-1)),
        'Cartan与提升交换':madd(mmul(cartan,lift),mscale(mmul(lift,cartan),-1)),
    }
    for name,value in equations.items():assert zero(value),name
    assert scale(power(negative,2)[2][0],2)==c
    weights=(0,-2,-4)
    for op,shift in [(positive,2),(negative,-2)]:
        for i in range(3):
            for j in range(3):
                if op[i][j]:assert weights[i]==weights[j]+shift
    result={'状态':'通过','系数环':'F_3[c]；c为不定元，非有限取值测试','已核对关系':list(equations),'二阶divided power作用':'X_-alpha^(2)e=c v_2','提升行列式':'c^2','整数Cartan权':[0,-2,-4],'范围':'仅核验教学用SL2三维扩张参数模型；一般G的Ext定理由笔记中的证明给出'}
    root=Path(__file__).resolve().parents[1]
    (root/'核验数据/扩张参数算例核验结果.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
