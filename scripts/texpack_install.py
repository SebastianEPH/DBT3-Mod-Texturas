#!/usr/bin/env python3
"""Installs your edited textures so the game uses them, naming each one as the game expects.

    python3 port/tools/texpack_install.py [--game <folder>] [--work <folder>] [--dry-run]

Put your edited pictures in <work>/selected-images/, each keeping the file name it had in extracted-images/png/
(for example tex_00061_256x512__ecac4e5e...-3ec0a55b...-00006613.png). They may be any size: a replacement of
four or eight times the original is the point of this. They are written into <game>/textures/, which is where
the game looks for them.

The game does not know textures by name but by a code made from their data, and a file is only used when it is
called <texture hash>-<palette hash>-<bits>.png (port/src/gs/gs_texpack.c). texpack_dump.py already put that
code in the file name after the `__`, so each picture carries its own identity and nothing else is needed. For
pictures made by an older version of that script (no code in the name), the code is looked up the old way: by
pairing extracted-images/texturas.log with the dumped .rgba files in order.

The alpha is rescaled back to the game's convention (0xFF opaque becomes 0x80), the reverse of texpack_dump.py.
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
CODE_IN_NAME = re.compile(r"__([0-9a-fA-F]+-[0-9a-fA-F]+-[0-9a-fA-F]+)$")
SIZE = re.compile(r"_(\d+)x(\d+)(?:__|\.)")
LOG = re.compile(r"^texpack: (?:found|missing)\s+(\d+)x(\d+)\s+\d+-bit\s+([0-9a-fA-F]+-[0-9a-fA-F]+-[0-9a-fA-F]+)")


def codes_from_log(dump):
    """{stem of a dumped file: code}, for pictures whose name carries no code (older runs)."""
    log_path = dump / "texturas.log"
    if not log_path.is_file():
        return {}
    log = []
    for line in log_path.read_text(errors="replace").splitlines():
        m = LOG.match(line.strip())
        if m:
            log.append((int(m.group(1)), int(m.group(2)), m.group(3)))
    out = {}
    for raw, (lw, lh, code) in zip(sorted(dump.glob("*.rgba")), log):
        m = re.search(r"_(\d+)x(\d+)\.rgba$", raw.name)
        if m and (int(m.group(1)), int(m.group(2))) == (lw, lh):
            out[raw.stem] = code
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=GAME, help="folder of the installed game")
    ap.add_argument("--work", help="working folder holding extracted-images/ and selected-images/ (default: the game's)")
    ap.add_argument("--dry-run", action="store_true", help="say what it would install, write nothing")
    args = ap.parse_args()

    game = pathlib.Path(args.game)
    work = pathlib.Path(args.work) if args.work else game
    mine, dump = work / "selected-images", work / "extracted-images"
    textures = game / "textures"      # always the game's own: that is where it looks
    if not mine.is_dir():
        mine.mkdir(parents=True, exist_ok=True)
        raise SystemExit(f"{mine} was empty, I made it. Put your edited pictures there and run this again.")

    old_way = None    # built only if some picture needs it
    done = skipped = 0
    for p in sorted(list(mine.glob("*.png")) + list(mine.glob("*.PNG"))):
        m = CODE_IN_NAME.search(p.stem)
        code = m.group(1) if m else None
        if code is None:
            if old_way is None:
                old_way = codes_from_log(dump)
            code = old_way.get(p.stem)
        if code is None:
            print(f"   {p.name}: SKIPPED, its name carries no code. Dump the textures again (step 1 and 2) "
                  f"and copy the picture from extracted-images/png as it is named there.")
            skipped += 1
            continue
        im = Image.open(p).convert("RGBA")
        r, g, b, a = im.split()
        a = a.point(lambda v: round(v * 128 / 255))   # back to the game's scale: 0xFF -> 0x80
        if not args.dry_run:
            textures.mkdir(parents=True, exist_ok=True)
            Image.merge("RGBA", (r, g, b, a)).save(textures / f"{code}.png")
        print(f"   {p.name}  {im.width}x{im.height}  ->  {code}.png")
        done += 1

    what = "would install" if args.dry_run else "installed"
    print(f"\n{what} {done} textures in {textures}" + (f", skipped {skipped}" if skipped else ""))
    if done and not args.dry_run:
        print("Start the game normally. To undo, delete those files from textures/.")


main()
