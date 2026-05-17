#!/usr/bin/env python3
import os, re, sys, glob

def fix_harfbuzz():
    base = os.path.join(os.getcwd(), ".buildozer")
    if not os.path.isdir(base):
        print("No .buildozer dir at", base)
        return 0
    count = 0
    for root, dirs, files in os.walk(base):
        for f in files:
            if f != "hb-ft.cc" or "SDL2_ttf" not in root:
                continue
            path = os.path.join(root, f)
            with open(path) as fh:
                content = fh.read()
            if "reinterpret_cast<FT_Generic_Finalizer>" in content:
                print("OK:", path)
                count += 1
                continue
            content = re.sub(r"\(FT_Generic_Finalizer\)\s*\(", "reinterpret_cast<FT_Generic_Finalizer>(", content)
            content = re.sub(r"\(FT_Generic_Finalizer\)\s+(hb_ft_face_finalize|_release_blob|hb_free)", r"reinterpret_cast<FT_Generic_Finalizer>(\1)", content)
            with open(path, "w") as fh:
                fh.write(content)
            print("FIX:", path)
            count += 1
    return count

if __name__ == "__main__":
    c = fix_harfbuzz()
    print(f"Total: {c}")
    sys.exit(0 if c > 0 else 1)

