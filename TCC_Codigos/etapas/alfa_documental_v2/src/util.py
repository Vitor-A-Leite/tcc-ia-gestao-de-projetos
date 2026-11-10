import hashlib
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
