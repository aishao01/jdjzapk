#!/usr/bin/env python3
"""Patch harfbuzz Android.mk to add -Wno-error=cast-function-type-strict."""
import os

cwd = os.getcwd()
print(f'Searching in: {cwd}')

for root, dirs, files in os.walk(cwd):
    for f in files:
        if f != 'Android.mk':
            continue
        path = os.path.join(root, f)
        if 'harfbuzz' not in path and 'SDL2_ttf' not in path:
            continue
        
        with open(path) as fh:
            content = fh.read()
        
        if 'Wno-error=cast-function-type-strict' in content:
            print(f'Already patched: {path}')
            continue
        
        lines = content.split('\n')
        changed = False
        for i, line in enumerate(lines):
            if 'LOCAL_CFLAGS' in line and ('+=' in line or ':=' in line):
                if '-Wno-error=cast-function-type-strict' not in line:
                    lines[i] = line.rstrip() + ' -Wno-error=cast-function-type-strict'
                    changed = True
        
        if changed:
            with open(path, 'w') as fh:
                fh.write('\n'.join(lines))
            print(f'Patched: {path}')
        else:
            print(f'No LOCAL_CFLAGS found in: {path}')

print('Done')
