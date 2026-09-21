"""新笔记本的数学复核附件：交换递推、对偶交织与局部核像。
不以有限参数检查代替正文的一般证明，不改动Albus资料。
"""
from pathlib import Path
from math import comb
import json

def choose(n,k):
    if k<0:return 0
    if n<0:return (-1)**k*comb(k-n-1,k)
    return comb(n,k) if k<=n else 0

def action(kind,op,s,i,weight,p,r):
    size=p**r
    if kind=='偶根':
        j=i+s if op=='负偶' else i-s
        c=choose(i+s,s) if op=='负偶' else choose(weight-i+s,s)
        return (j,c%p) if 0<=j<size and c%p else None
    index,odd=divmod(i,2)
    if op=='负偶': j,b,c=index+s,odd,choose(index+s,s)
    elif op=='正偶':j,b,c=index-s,odd,choose(weight-odd-index+s,s)
    elif op=='正奇':
        j,b,c=(index,0,2*(weight-index)) if odd else (index-1,1,1)
    else:
        j,b,c=(index+1,0,-2*(index+1)) if odd else (index,1,1)
    return (2*j+b,c%p) if 0<=j<size and c%p else None

def main():
    recurrence=0
    for n in range(7):
        for m in range(7):
            for k in range(min(n+1,m)+1):
                for h in range(-10,11):
                    old=choose(h-m-n+2*k-2,k) if k<=min(n,m) else 0
                    prev=choose(h-m-n+2*(k-1),k-1) if k>=1 and k-1<=min(n,m) else 0
                    lhs=(n+1)*choose(h-m-(n+1)+2*k,k)
                    rhs=(n-k+1)*old+(h-m+k)*prev
                    assert lhs==rhs,(n,m,k,h,lhs,rhs)
                    recurrence+=1
    dual_counts={}
    for kind in ('偶根','非各向同性奇根'):
        cases=0;checks=0
        for p,r in ((3,1),(3,2),(3,3),(5,1),(5,2)):
            size=p**r;dimension=size if kind=='偶根' else 2*size
            for weight in range(-1,size+1):
                dual_weight=-weight+(2*size-2 if kind=='偶根' else 2*size-1)
                def identification(i):
                    if kind=='偶根':return size-1-i
                    a,b=divmod(i,2)
                    return 2*(size-1-a)+(1-b)
                ops=[(op,s) for op in ('正偶','负偶') for s in range(size)]
                if kind!='偶根':ops += [('正奇',1),('负奇',1)]
                for op,s in ops:
                    parity=int('奇' in op)
                    old=[action(kind,op,s,i,weight,p,r) for i in range(dimension)]
                    dual=[{} for i in range(dimension)]
                    for src,item in enumerate(old):
                        if item is None:continue
                        dst,c=item
                        f_parity=dst%2 if kind!='偶根' else 0
                        sign=(-1)**(1+f_parity) if parity else (-1)**s
                        dual[dst][src]=(sign*c)%p
                    for i in range(dimension):
                        item=action(kind,op,s,i,dual_weight,p,r)
                        lhs={identification(item[0]):item[1]} if item else {}
                        assert lhs==dual[identification(i)],(kind,p,r,weight,op,s,i,lhs,dual[identification(i)])
                        checks+=1
                cases+=1
        dual_counts[kind]={'最高权参数组':cases,'交织等式':checks}
    # 分开的原核、变权像、终端条件；包含全部边界。
    terminal_counts={}
    for kind in ('偶根','非各向同性奇根'):
        cases=0
        for p,r in ((3,1),(3,2),(3,3),(5,1),(5,2),(7,2)):
            size=p**r
            for d in range(size):
                digits=[(d//p**j)%p for j in range(r)]
                if kind=='偶根':
                    if not d:
                        assert all(choose(d+i,i)%p for i in range(size));cases+=1;continue
                    nu=next(j for j,x in enumerate(digits) if x)
                    original={i for i in range(size) if choose(d+i,i)%p==0}
                    shift=(p-digits[nu])*p**nu
                    image={i+shift for i in range(size-shift) if choose(i+shift,shift)%p}
                    kernel={i for i in range(size) if i+shift>=size or choose(i+shift,shift)%p==0}
                    next_shift=digits[nu]*p**nu
                    next_image={i+next_shift for i in range(size-next_shift) if choose(i+next_shift,next_shift)%p}
                    assert kernel==next_image and image<=original
                    assert (original==image)==(d==digits[nu]*p**nu)
                else:
                    original={2*i for i in range(size) if choose(d,i)%p==0}
                    original|={2*i+1 for i in range(size) if 2*d*choose(d-1,i)%p==0}
                    image={2*i for i in range(size) if i%p>=digits[0]+1}
                    image|={2*i+1 for i in range(size) if i%p>=digits[0]}
                    assert image<=original
                    assert (image==original)==all(x==p-1 for x in digits[1:])
                cases+=1
        terminal_counts[kind]=cases
    data={'日期':'2026-09-21','状态':'通过','交换公式递推检查':recurrence,
          '对偶公式与奇性':dual_counts,'正合列终端参数组':terminal_counts,
          '范围':'按正文作用独立实现后检查对偶与递推相容性；不宣称一般群的形式化证明或外部独立审定。'}
    p=Path(__file__).resolve().parents[1]/'核验数据/高阶核自足稿数学复核.json'
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
