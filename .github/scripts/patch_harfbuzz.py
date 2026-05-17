#!/usr/bin/env python3
"""Fix hb-ft.cc: replace C-style FT_Generic_Finalizer casts with reinterpret_cast."""
import os, re

cwd = os.getcwd()
count = 0

for root, dirs, files in os.walk(cwd):
    for f in files:
        if f == 'hb-ft.cc' and 'SDL2_ttf' in root:
            path = os.path.join(root, f)
            with open(path) as fh:
                content = fh.read()
            
            if 'reinterpret_cast<FT_Generic_Finalizer>' in content:
                print(f'Already fixed: {path}')
                count += 1
                continue
            
            # Replace C-style (FT_Generic_Finalizer) casts with reinterpret_cast
            # There are 3 forms:
            # 1. (FT_Generic_Finalizer)(expr)
            # 2. (FT_Generic_Finalizer)hb_free
            # 3. (FT_Generic_Finalizer) fn
            for pattern in [
                (r'\(FT_Generic_Finalizer\)\s*\(', 'reinterpret_cast<FT_Generic_Finalizer>('),
                (r'\(FT_Generic_Finalizer\)\s*hb_free', 'reinterpret_cast<FT_Generic_Finalizer>(reinterpret_cast<void(*)(void*)>(hb_free))'),
            ]:
                old, new = pattern
                content = re.sub(old, new, content)
            
            # Handle remaining C-style casts that weren't matched
            # Simple: replace any remaining (FT_Generic_Finalizer)xxx
            content = re.sub(
                r'\(FT_Generic_Finalizer\)\s*(\w[\w<>*&:]*)',
                r'reinterpret_cast<FT_Generic_Finalizer>(\1)',
                content
            )
            
            with open(path, 'w') as fh:
                fh.write(content)
            print(f'Fixed: {path}')
            count += 1
            
            # Also delete compiled objects to force recompile
            build_root = root  # .../SDL2_ttf/external/harfbuzz/src
            obj_base = os.path.abspath(os.path.join(build_root, '..', '..', '..', '..', 'obj'))
            print(f'Cleaning object files under: {obj_base}')
            if os.path.isdir(obj_base):
                for obj_root, obj_dirs, obj_files in os.walk(obj_base):
                    for obj_f in obj_files:
                        if 'harfbuzz' in obj_root and obj_f.endswith('.o'):
                            os.unlink(os.path.join(obj_root, obj_f))
                            print(f'  Removed: {obj_f}')

print(f'Total: {count}')
