#!/usr/bin/env python3
"""Upscales the textures you picked, keeping the originals beside them.

    python3 port/tools/texpack_upscale.py [--game <folder>] [--scale 4] [--model realesrgan-x4plus-anime]

Takes every .png directly inside <game>/selected-images/, moves it to <game>/selected-images/originals/ and writes
the upscaled version back under the same name. So after a run, selected-images/ holds the big versions (which is
what texpack_install.py installs) and selected-images/originals/ holds exactly what came out of the game.

Needs the portable Real-ESRGAN (realesrgan-ncnn-vulkan.exe), which you download yourself from its own page
(https://github.com/xinntao/Real-ESRGAN/releases): it runs on the graphics card through Vulkan and installs
nothing. It is looked for in a `realesrgan` folder next to the tools, beside this script, in
Downloads/herramientas/realesrgan/, on the PATH, or wherever --exe says; when it is nowhere, this step says so
and stops. Nothing is ever downloaded on your behalf.

Models that ship with it: realesrgan-x4plus-anime (drawn art: this game), realesrgan-x4plus (photos),
realesr-animevideov3-x2 / -x3 / -x4. A scale of 8 is done as 4 then 2, since no model does 8 in one go.

Running it again only upscales what is still in selected-images/: a file already done (its original is in
originals/ and its name is taken) is left alone unless --force is given.
"""
import argparse
import pathlib
import shutil
import subprocess
import sys

_HERE = pathlib.Path(__file__).resolve().parent
GAME = str(_HERE.parents[1])
HOME = _HERE.parent / "realesrgan"      # where it is expected, if you put it next to the tools
EXE_PLACES = [
    HOME / "realesrgan-ncnn-vulkan.exe",
    _HERE / "realesrgan-ncnn-vulkan.exe",
    pathlib.Path.home() / "Downloads" / "herramientas" / "realesrgan" / "realesrgan-ncnn-vulkan.exe",
]


def find_exe(given):
    if given:
        p = pathlib.Path(given)
        if p.is_file():
            return p
        raise SystemExit(f"{p}: not there")
    for p in EXE_PLACES:
        if p.is_file():
            return p
    found = shutil.which("realesrgan-ncnn-vulkan")
    if found:
        return pathlib.Path(found)
    raise SystemExit(
        "This step needs Real-ESRGAN, and it is not here.\n"
        "\n"
        "  Get the portable build for Windows (realesrgan-ncnn-vulkan) from its own page,\n"
        "      https://github.com/xinntao/Real-ESRGAN/releases\n"
        "  and unzip it into:\n"
        f"      {HOME}\n"
        "  Or give its path with  --exe <path>\n"
        "\n"
        "  This step is optional: you can upscale the pictures with any other program\n"
        "  (Upscayl, chaiNNer, Photoshop, GIMP) and go straight to step 3.")


def run(exe, model_dir, model, src, dst, scale):
    cmd = [str(exe), "-i", str(src), "-o", str(dst), "-n", model, "-s", str(scale), "-f", "png"]
    if model_dir.is_dir():
        cmd += ["-m", str(model_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not dst.is_file():
        tail = (r.stderr or r.stdout or "").strip().splitlines()
        raise SystemExit(f"{src.name}: upscaling failed\n   " + "\n   ".join(tail[-4:]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--game", default=GAME, help="folder of the installed game")
    ap.add_argument("--scale", type=int, default=4, choices=[2, 3, 4, 8], help="how many times bigger (default 4)")
    ap.add_argument("--model", default="realesrgan-x4plus-anime", help="model name (default: the anime one)")
    ap.add_argument("--exe", help="path of realesrgan-ncnn-vulkan.exe")
    ap.add_argument("--force", action="store_true", help="upscale again files that were done already")
    ap.add_argument("--work", help="working folder holding selected-images/ (default: the game's)")
    args = ap.parse_args()

    mine = (pathlib.Path(args.work) if args.work else pathlib.Path(args.game)) / "selected-images"
    originals = mine / "originals"
    if not mine.is_dir():
        mine.mkdir(parents=True, exist_ok=True)
        raise SystemExit(f"{mine} was empty, I made it. Copy the pictures you want to improve there "
                         f"(from extracted-images\\png) and run this again.")
    exe = find_exe(args.exe)
    model_dir = exe.parent / "models"

    todo = sorted(p for p in mine.glob("*.png") if p.is_file())
    if not todo:
        raise SystemExit(f"no .png directly in {mine}. Copy there the ones you want to improve.")
    originals.mkdir(exist_ok=True)

    try:
        from PIL import Image
    except ImportError:                   # install it once, by itself: it is the only library needed
        print("Pillow (the image library) is missing; installing it once ...")
        if subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pillow"]).returncode != 0:
            raise SystemExit("could not install Pillow. Do it by hand with:  python -m pip install pillow")
        from PIL import Image
        print("   done")
    done = skipped = 0
    for p in todo:
        kept = originals / p.name
        if kept.is_file() and not args.force:
            print(f"   {p.name}: already done (its original is in originals/)")
            skipped += 1
            continue
        before = Image.open(p).size
        shutil.move(str(p), str(kept))
        if args.scale == 8:
            tmp = mine / ("_tmp_" + p.name)
            run(exe, model_dir, args.model, kept, tmp, 4)
            run(exe, model_dir, "realesr-animevideov3-x2", tmp, p, 2)
            tmp.unlink(missing_ok=True)
        else:
            run(exe, model_dir, args.model, kept, p, args.scale)
        after = Image.open(p).size
        print(f"   {p.name}: {before[0]}x{before[1]} -> {after[0]}x{after[1]}")
        done += 1

    print(f"\nupscaled {done} pictures with {args.model} x{args.scale}" + (f", {skipped} already done" if skipped else ""))
    print(f"   the big ones stay in {mine}")
    print(f"   the untouched originals are in {originals}")
    print("Now run 3-install-textures.bat to put them in the game.")


main()
