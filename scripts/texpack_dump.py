#!/usr/bin/env python3
"""Turns the raw textures of BT3_TEX_DUMP into PNGs you can look at and edit.

    python3 port/tools/texpack_dump.py [--game <folder>] [--work <folder>] [--keep-raw]

Reads <work>/extracted-images/*.rgba (written by the game with BT3_TEX_DUMP set) and writes <work>/extracted-images/png/.
The size of each texture is in its file name, which is how the raw pixels are given a shape. The .rgba files
are deleted afterwards unless --keep-raw: everything needed is in the PNG by then.

Each PNG is named  tex_<n>_<w>x<h>__<code>.png,  where <code> is the name the game expects a replacement of that
texture to have (<texture hash>-<palette hash>-<bits>, see port/src/gs/gs_texpack.c). The code comes from
extracted-images/texturas.log, which the game writes with BT3_TEX_LOG set: it looks a texture up before dumping it, so
the Nth line belongs to the Nth dumped file, and the size in both is checked before they are paired. Carrying
the code in the name means texpack_install.py needs neither the log nor the raw files, and a picture kept from
an older session still installs correctly.

The alpha is rescaled: the game's textures use the GS convention where 0x80 means opaque, so a viewer or an
image editor would show every texture half transparent. Here 0x80 becomes 0xFF, which is what an editor and an
upscaler expect. texpack_install.py does the reverse when a replacement goes back into the game.
"""
import argparse
import pathlib
import re

try:
    from PIL import Image
except ImportError:                       # install it once, by itself: it is the only library needed
    import subprocess as _sp, sys as _sys
    print("Pillow (the image library) is missing; installing it once ...")
    if _sp.run([_sys.executable, "-m", "pip", "install", "--quiet", "pillow"]).returncode != 0:
        raise SystemExit("could not install Pillow. Do it by hand with:  python -m pip install pillow")
    try:
        from PIL import Image
    except ImportError:
        raise SystemExit("Pillow installed but still not importable; try closing and opening the console")
    print("   done")

GAME = str(pathlib.Path(__file__).resolve().parents[2])
SIZE = re.compile(r"_(\d+)x(\d+)\.rgba$")
# texpack: missing 512x256 8-bit 1dd4c76113969303-56e3d4469d2ad392-00005e54
LOG = re.compile(r"^texpack: (?:found|missing)\s+(\d+)x(\d+)\s+\d+-bit\s+([0-9a-fA-F]+-[0-9a-fA-F]+-[0-9a-fA-F]+)")


def read_log(path):
    """[(w, h, code)] of every texture the game looked up, in order."""
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(errors="replace").splitlines():
        m = LOG.match(line.strip())
        if m:
            out.append((int(m.group(1)), int(m.group(2)), m.group(3)))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=GAME, help="folder of the installed game")
    ap.add_argument("--work", help="working folder holding extracted-images/ and selected-images/ (default: the game's)")
    ap.add_argument("--keep-raw", action="store_true", help="do not delete the .rgba files afterwards")
    ap.add_argument("--ensure-marker", action="store_true",
                    help="only make sure <game>/textures/0-0-0.png exists, then stop. The game writes the "
                         "codes we need (BT3_TEX_LOG) only while its replacement system is on, and that needs "
                         "at least one replacement file in textures/; this one-pixel PNG replaces nothing.")
    args = ap.parse_args()

    if args.ensure_marker:
        marker = pathlib.Path(args.game) / "textures" / "0-0-0.png"
        if marker.is_file():
            return
        marker.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGBA", (1, 1), (0, 0, 0, 0)).save(marker)
        print(f"made {marker} (it switches the game's texture replacement on)")
        return

    work = pathlib.Path(args.work) if args.work else pathlib.Path(args.game)
    dump = work / "extracted-images"
    if not dump.is_dir():
        raise SystemExit(f"{dump}: not there. Run 1-extract-textures.bat first.")
    out = dump / "png"
    out.mkdir(exist_ok=True)

    raws = sorted(dump.glob("*.rgba"))
    log = read_log(dump / "texturas.log")
    if not log:
        print("WARNING: extracted-images/texturas.log is empty, so the pictures get no code in their name and")
        print("         texpack_install.py will not be able to install them. Run step 1 again.")

    ok = bad = named = 0
    for n, p in enumerate(raws):
        m = SIZE.search(p.name)
        if not m:
            bad += 1
            continue
        w, h = int(m.group(1)), int(m.group(2))
        d = p.read_bytes()
        if len(d) < w * h * 4:
            bad += 1
            continue
        code = None
        if n < len(log) and (log[n][0], log[n][1]) == (w, h):
            code = log[n][2]
            named += 1
        r, g, b, a = Image.frombytes("RGBA", (w, h), d[:w * h * 4]).split()
        a = a.point(lambda v: 255 if v >= 128 else min(255, round(v * 255 / 128)))
        stem = f"tex_{n:05d}_{w}x{h}" + (f"__{code}" if code else "")
        Image.merge("RGBA", (r, g, b, a)).save(out / (stem + ".png"))
        ok += 1

    if not args.keep_raw:
        for p in raws:
            p.unlink()

    print(f"{ok} textures -> {out}" + (f"   ({bad} could not be read)" if bad else ""))
    print(f"   {named} of them carry the game's code in the file name (the ones that can be installed)")
    if not args.keep_raw:
        print(f"   the .rgba files were deleted; only PNGs are left")
    print("\nNow: look in extracted-images/png, and copy the ones you want to improve into")
    print(f"   {work / 'selected-images'}")
    print("WITHOUT changing their names. Then run 2-upscale-images.bat")


main()
