import subprocess

class CO:
    def __init__(self, cmd):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
        self._read(186)
        self.buf = b''
    def _read(self, cnt):
        ans = b''
        while cnt > 0:
            b = self.p.stdout.read(cnt)
            assert b
            ans += b
            cnt -= len(b)
        return ans
    def send_query(self, b):
        assert len(b) in range(1, 7) or (len(b) == 8 and b[-2:] == b'\0\0')
        if len(b) == 6:
            b += b'\0\0'
        self.buf += b'1\n'+b
    def flush(self):
        assert self.p.stdin.write(self.buf) == len(self.buf)
        self.p.stdin.flush()
        self.buf = b''
    def fetch_answer(self):
        self.p.stdin.flush()
        assert self._read(12) == b'read where: '
        d1 = self._read(8)
        d2 = self._read(8)
        if d2 == b'trary re':
            self._read(32)
            return None
        else:
            self._read(40)
            return d1
    def query_multiple(self, q):
        assert all(len(i) in (6, 8) for i in q[:-1])
        for i in q: self.send_query(i)
        self.flush()
        return [self.fetch_answer() for i in q]
    def query(self, q):
        return self.query_multiple([q])[0]
    def send_write(self, addr, value):
        self.buf += b'2\n'+addr+value
    def verify_write(self):
        self.p.stdin.flush()
        assert self._read(13) == b'write where: '
        assert self._read(12) == b'write what: '
        self._read(48)
    def write_multiple(self, pairs):
        for k, v in pairs: self.send_write(k, v)
        self.flush()
        for k, v in pairs: self.verify_write()
    def write(self, k, v):
        self.write_multiple([k, v])
    def close(self):
        self.buf += b'3\n'
        self.flush()
