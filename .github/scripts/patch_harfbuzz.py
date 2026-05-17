#!/usr/bin/env python3
"""Patch hb-ft.cc in .buildozer to suppress clang cast-function-type-strict errors."""
import os

buildozer_dir = os.getcwd()
print(f'Searching in: {buildozer_dir}/.buildozer')
count = 0
for root, dirs, files in os.walk(buildozer_dir):
    for f in files:
        if f == 'hb-ft.cc':
            path = os.path.join(root, f)
            # Skip if not in SDL2_ttf build path
            if 'SDL2_ttf' not in path:
                continue
            with open(path) as fh:
                content = fh.read()
            if '#pragma clang diagnostic' not in content:
                pragma = '#pragma clang diagnostic ignored "-Wcast-function-type-strict"\n'
                with open(path, 'w') as fh:
                    fh.write(pragma + content)
                print(f'Patched: {path}')
                count += 1
            else:
                print(f'Already patched: {path}')

print(f'Total files patched: {count}')
