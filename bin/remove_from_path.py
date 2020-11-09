'''
    Usage:
        python remove_from_env.py $PATH $TO_BE_REMOVED
    returns $PATH without paths starting with $TO_BE_REMOVED
'''
from __future__ import print_function
import sys

ENV = sys.argv[1]
REMOVE = sys.argv[2]

new_path = []
for path in ENV.split(':'):
    if path.startswith(REMOVE):
        continue
    new_path.append(path)
print(':'.join(new_path))
