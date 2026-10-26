"""エピソードをまとめてビルドする。

    python3 build_all.py            # 全エピソード
    python3 build_all.py ep02 ep05  # 名前が前方一致するものだけ
"""
import glob
import importlib.util
import os
import sys

from concurrent.futures import ThreadPoolExecutor

import engine

ROOT = os.path.dirname(os.path.abspath(__file__))


def load(path):
    spec = importlib.util.spec_from_file_location(os.path.basename(path)[:-3], path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(prefixes):
    paths = sorted(glob.glob(os.path.join(ROOT, "episodes", "ep*.py")))
    if prefixes:
        paths = [p for p in paths if any(os.path.basename(p).startswith(x) for x in prefixes)]
    eps = [load(p) for p in paths]
    # 先にナレーションを並列で用意しておく
    texts = [c[3] if len(c) > 3 and c[3] else c[2].replace("\n", "") for ep in eps for c in ep.CUTS]
    with ThreadPoolExecutor(4) as pool:
        list(pool.map(engine.tts, texts))
    short = [ep.SLUG for ep in eps if engine.build(ep) < engine.MIN_SECONDS]
    if short:
        print("61秒未満:", ", ".join(short))


if __name__ == "__main__":
    main(sys.argv[1:])
