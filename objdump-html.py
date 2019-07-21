import html, sys

def istoken(s):
    return s.replace('_', '').isalnum()

def tokenize(s):
    ans = ['']
    for c in s:
        if istoken(ans[-1]) and istoken(c):
            ans[-1] += c
        else:
            ans.append(c)
    if ans[0] == '':
        del ans[0]
    return ans

def ishex(i):
    try: int(i, 16)
    except ValueError: return False
    return True

def isreg(i):
    return i[:1] == '%' and i[1:].isalnum()

def isvar(i):
    return '(' in i and ')' in i

def postprocess(s):
    ans = []
    for i in s:
        if ans and ans[-1] == '%' and i.isalnum():
            ans[-1] += i
        elif len(ans) >= 3 and i == ')' and ans[-2] == '(' and ans[-1] in ('%ebp', '%rbp') and ishex(ans[-3]):
            for i in range(2):
                x = ans.pop()
                ans[-1] += x
            if len(ans) >= 2 and ans[-2] == '-':
                x = ans.pop()
                ans[-1] += x
            ans[-1] += ')'
        else:
            ans.append(i)
    return ans

def preprocess_tabs(s):
    ans = ''
    pos = 0
    for c in s:
        if c == '\t':
            while pos % 8:
                ans += ' '
                pos += 1
            continue
        ans += c
        pos += 1
        if c == '\n': pos = 0
    return ans

page = '''\
<html>
<head>
<style>
.bistate:before
{
    content: attr(data-normal);
}

.bistate:hover:before
{
    content: attr(data-hover);
}

.reg
{
    color: green;
}

.var
{
    color: orange;
}

.hex
{
    color: blue;
}
</style>
<script>
function underline(cls)
{
    var x = document.getElementsByClassName(cls);
    for(var i = 0; i < x.length; i++)
        x[i].style.textDecoration = 'underline';
}

function derline(cls)
{
    var x = document.getElementsByClassName(cls);
    for(var i = 0; i < x.length; i++)
        x[i].style.textDecoration = '';
}

function rename(cls)
{
    derline(cls);
    var to_what = prompt(cls);
    var x = document.getElementsByClassName(cls);
    for(var i = 0; i < x.length; i++)
        x[i].setAttribute('data-normal', to_what);
}
</script>
</head>
<body>
<pre>'''

def dump_mem(od_lines):
    mem = {}
    for i in od_lines:
        i = i.split('\t')
        x = i[0].strip()
        if x and x[-1] == ':' and ishex(x[:-1]):
            addr = int(x[:-1], 16)
            try: bts = bytes.fromhex(''.join(i[1].split()))
            except ValueError: continue
            for i, j in enumerate(bts): mem[addr + i] = j
    return mem

reg_alias = {}

for i in 'abcd':
    reg_alias[i+'l'] = reg_alias[i+'h'] = 'e%sx'%i

for i in ('ax', 'bx', 'cx', 'dx', 'sp', 'bp', 'si', 'di'):
    reg_alias[i] = reg_alias['r'+i] = 'e'+i

reg_cls = {}
reg_cls_cnt = 0

with open(sys.argv[1], 'r') as file:
    od0 = file.read()
    od = postprocess(tokenize(preprocess_tabs(od0)))
    od_lines = od0.split('\n')

mem = dump_mem(od_lines)

def strat(addr):
    ans = b''
    while ans[-1:] != b'\0':
        try: ans += bytes((mem[addr],))
        except KeyError: return None
        addr += 1
    return ans[:-1]

mov_lea_state = 0
wsp_state = 0

for i in od:
    if i in ('mov', 'lea') and mov_lea_state == 0:
        mov_lea_state = 1
    elif i == ',' and mov_lea_state == 1:
        mov_lea_state = 2
    elif i == '\n':
        mov_lea_state = 0
    if i == '\n':
        if wsp_state:
            for j in list(reg_cls):
                if isvar(j): del reg_cls[j]
        wsp_state = 1
    elif i and not i.isspace():
        wsp_state = 0
    if isreg(i) or isvar(i):
        cls0 = 'reg' if isreg(i) else 'var'
        ii = i
        if isreg(ii):
            ii = '%'+reg_alias.get(ii[1:], ii[1:])
            if ii in reg_cls and mov_lea_state == 2:
                del reg_cls[ii]
        if ii in reg_cls:
            cls = reg_cls[ii]
        else:
            cls = reg_cls[ii] = 'reg_%d'%reg_cls_cnt
            reg_cls_cnt += 1
        rename = ''
        if cls0 == 'var':
            rename = ' ondblclick="rename(\'{cls}\')"'.format(cls=cls)
        page += '<span class="bistate {cls0} {cls}" onmouseover="underline(\'{cls}\')" onmouseout="derline(\'{cls}\')"{rename} data-normal="{data}" data-hover="{data}"></span>'.format(cls0=cls0, cls=cls, data=html.escape(i), rename=rename)
    elif ishex(i):
        s = strat(int(i, 16))
        if s != None: page += '<span class="bistate hex" data-normal="{orig}" data-hover="{strat}"></span>'.format(orig=html.escape(i), strat=html.escape(repr(s)))
        else: page += '<span class="hex">'+html.escape(i)+'</span>'
    else:
        page += html.escape(i)

page += '</body>\n</html>'
print(page)
