#!/usr/bin/env python3
"""Clone p4a v2024.01.21 and patch SDL2_ttf recipe to fix hb-ft.cc."""
import os, subprocess, sys

cwd = os.getcwd()
p4a_dir = os.path.join(cwd, '.buildozer', 'android', 'platform', 'python-for-android')

# Clone p4a
if not os.path.isdir(p4a_dir):
    print("Cloning p4a v2024.01.21...")
    r = subprocess.run(
        ['git', 'clone', '--branch', 'v2024.01.21', '--depth', '1',
         'https://github.com/kivy/python-for-android.git', p4a_dir],
        capture_output=True, text=True, timeout=120)
    print(r.stdout[-200:] if r.stdout else "")
    if r.returncode != 0:
        print(f"Clone failed: {r.stderr[:200]}")
        sys.exit(1)
else:
    print("p4a already cloned")

# Patch the SDL2_ttf recipe
recipe = os.path.join(p4a_dir, 'pythonforandroid', 'recipes', 'sdl2_ttf', '__init__.py')
print(f"Patching recipe: {recipe}")

with open(recipe) as f:
    content = f.read()

if 'PATCHED_BY_HERMES' in content:
    print("Recipe already patched")
else:
    # Add prebuild_arch method that fixes hb-ft.cc
    patch_code = '''
    # PATCHED_BY_HERMES - fix clang cast-function-type-strict errors
    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        import os
        src = os.path.join(self.get_build_dir(arch.arch), 'external', 'harfbuzz', 'src', 'hb-ft.cc')
        if os.path.exists(src):
            import re
            with open(src) as f:
                c = f.read()
            c = re.sub(r'\\(FT_Generic_Finalizer\\)\\s*\\\\(', 'reinterpret_cast<FT_Generic_Finalizer>(', c)
            c = re.sub(r'\\(FT_Generic_Finalizer\\)\\s+(\\w+)', r'reinterpret_cast<FT_Generic_Finalizer>(\\1)', c)
            with open(src, 'w') as f:
                f.write(c)
            print("prebuild_arch: patched hb-ft.cc")
'''

    # Insert after class definition
    marker = 'class Sdl2TtfRecipe'
    if marker in content:
        content = content.replace(marker, marker + patch_code)
        with open(recipe, 'w') as f:
            f.write(content)
        print("Recipe patched successfully")
    else:
        print(f"ERROR: Could not find '{marker}' in recipe")
        sys.exit(1)

# Add p4a.source_dir to buildozer.spec if not already there
spec_path = os.path.join(cwd, 'buildozer.spec')
with open(spec_path) as f:
    spec = f.read()

entry = f'p4a.source_dir = {p4a_dir}'
if entry not in spec:
    with open(spec_path, 'a') as f:
        f.write(f'\n# PATCHED_BY_HERMES\n{entry}\n')
    print(f"Added p4a.source_dir to buildozer.spec")
else:
    print("p4a.source_dir already in spec")

print("Pre-build setup complete!")
