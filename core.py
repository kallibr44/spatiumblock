import hashlib

def get_hash(string):
    hash = hashlib.sha256(string).hexdigest()
    return hash