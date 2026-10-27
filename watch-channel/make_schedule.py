"""videos/*.txt と STRATEGY.md のカレンダーから、予約投稿の一覧を書き出す。

    python3 make_schedule.py [開始日 YYYY-MM-DD] [時刻 HH:MM]  ->  tiktok/schedule.csv
"""
import csv
import datetime
import glob
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
WEEKDAYS = "月火水木金土日"


def titles():
    """STRATEGY.md のカレンダー表から {"ep01": "オメガが月に行った話", ...}"""
    text = open(os.path.join(ROOT, "STRATEGY.md"), encoding="utf-8").read()
    return dict(re.findall(r"^\| \d+ \| [^|]+ \| (ep\d+) \| ([^|]+?) \|", text, re.M))


def seconds(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return round(float(out.stdout))


def main():
    start = datetime.date.fromisoformat(sys.argv[1] if len(sys.argv) > 1 else "2026-10-28")
    time = sys.argv[2] if len(sys.argv) > 2 else "20:00"
    names = titles()
    rows = []
    for i, txt in enumerate(sorted(glob.glob(os.path.join(ROOT, "videos", "ep*.txt")))):
        slug = os.path.basename(txt)[:-4]
        caption = open(txt, encoding="utf-8").read().strip()
        day = start + datetime.timedelta(days=i)
        rows.append({
            "日": i + 1,
            "投稿日": f"{day.isoformat()}({WEEKDAYS[day.weekday()]})",
            "時刻(JST)": time,
            "動画ファイル": f"watch-channel/videos/{slug}.mp4",
            "タイトル": names.get(slug[:4], ""),
            "長さ(秒)": seconds(txt[:-4] + ".mp4"),
            "キャプション": caption,
            "AI生成ラベル": "オン",
            "状態": "",
        })
    with open(os.path.join(ROOT, "tiktok", "schedule.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} 本: {rows[0]['投稿日']} 〜 {rows[-1]['投稿日']} {time}")


if __name__ == "__main__":
    main()
