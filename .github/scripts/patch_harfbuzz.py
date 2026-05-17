#!/usr/bin/env python3
"""Fix hb-ft.cc: replace C-style FT_Generic_Finalizer casts with reinterpret_cast."""
import os, re

cwd = os.getcwd()
count = 0

for root, dirs, files in os.walk(cwd):
    for f in files:
        if f != 'hb-ft.cc' or 'SDL2_ttf' not in root:
            continue
        path = os.path.join(root, f)
        with open(path) as fh:
            content = fh.read()
        
        if 'reinterpret_cast<FT_Generic_Finalizer>' in content:
            print(f'Already fixed: {path}')
            continue
        
        # Replace C-style (FT_Generic_Finalizer) casts with reinterpret_cast
        # Pattern: (FT_Generic_Finalizer)(something) or (FT_Generic_Finalizer)something
        new_content = re.sub(
            r'\(FT_Generic_Finalizer\)\s*\(',
            'reinterpret_cast<FT_Generic_Finalizer>(',
            content
        )
        new_content = re.sub(
            r'\(FT_Generic_Finalizer\)(\s*\w+)',
            r'reinterpret_cast<FT_Generic_Finalizer>(\1)',
            new_content
        )
        # Also handle free cast
        new_content = re.sub(
            r'\(FT_Generic_Finalizer\)\s*hb_free',
            'reinterpret_cast<FT_Generic_Finalizer>(reinterpret_cast<void(*)(void*)>(hb_free))',
            new_content
        )
        
        if new_content != content:
            with open(path, 'w') as fh:
                fh.write(new_content)
            print(f'Fixed: {path}')
            count += 1
        else:
            print(f'No changes needed: {path}')

print(f'Total fixed: {count}')
