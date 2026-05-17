#!/usr/bin/env python3
"""Patch hb-ft.cc to mark as system header (suppress ALL warnings from this file)."""
import os

cwd = os.getcwd()
count = 0
for root, dirs, files in os.walk(cwd):
    for f in files:
        if f != 'hb-ft.cc':
            continue
        path = os.path.join(root, f)
        if 'SDL2_ttf' not in path:
            continue
        
        with open(path) as fh:
            content = fh.read()
        
        if '#pragma' in content or 'system_header' in content:
            print(f'Already patched: {path}')
            continue
        
        # Add system_header pragma at the very top
        pragma_lines = '''#if defined(__clang__)
#pragma clang system_header
#elif defined(__GNUC__) || defined(__GNUG__)
#pragma GCC system_header
#endif

'''
        with open(path, 'w') as fh:
            fh.write(pragma_lines + content)
        print(f'Patched: {path}')
        count += 1

print(f'Total: {count}')
