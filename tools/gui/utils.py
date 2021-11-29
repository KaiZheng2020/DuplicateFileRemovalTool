import hashlib
import os
import sys


def calc_md5(path):
    with open(path, 'rb') as f:
        md5obj = hashlib.md5()
        md5obj.update(f.read())
        hash = md5obj.hexdigest()
        return hash
