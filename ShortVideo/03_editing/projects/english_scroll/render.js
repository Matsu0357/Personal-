// render.html を Playwright で1コマずつ描いて、ffmpeg で動画にする。縦型 1080x1920
// 使い方（先に python3 build_audio.py 02）。回の番号を最初に書く:
//   node render.js 02                  → build_02/video.mp4（音声付き）
//   node render.js 02 --preview 1,8    → build_02/preview_1.jpg などの確認用画像
//   node render.js 02 --thumb          → build_02/cover.png（カバー画像）
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const FPS = 30;
const EP = /^\d+$/.test(process.argv[2] || "") ? process.argv[2] : "01";
const BUILD = path.join(__dirname, `build_${EP}`);

(async () => {
  const timeline = JSON.parse(fs.readFileSync(path.join(BUILD, "timeline.json"), "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto("file://" + path.join(__dirname, "render.html"));
  await page.evaluate(async () => {
    await document.fonts.load("700 50px Inter");
    await document.fonts.load("500 32px NotoJP");
    await document.fonts.load("900 72px NotoJP");
  });
  await page.evaluate(tl => window.init(tl), timeline);

  const grab = (t, type = "jpeg") => page.evaluate(([t, type]) => {
    window.renderFrame(t);
    return document.getElementById("c").toDataURL("image/" + type, 0.92).split(",")[1];
  }, [t, type]);

  if (process.argv.includes("--thumb")) {
    const png = await page.evaluate(() => { window.renderThumb(); return document.getElementById("c").toDataURL("image/png").split(",")[1]; });
    fs.writeFileSync(path.join(BUILD, "cover.png"), Buffer.from(png, "base64"));
    await browser.close();
    return;
  }

  const pi = process.argv.indexOf("--preview");
  if (pi > 0) {
    for (const t of process.argv[pi + 1].split(",").map(Number)) {
      fs.writeFileSync(path.join(BUILD, `preview_${t}.jpg`), Buffer.from(await grab(t), "base64"));
    }
    await browser.close();
    return;
  }

  const ff = spawn("ffmpeg", [
    "-loglevel", "error", "-y",
    "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-i", path.join(BUILD, "audio.wav"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000",  // SNS 向けの音量にそろえる
    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
    path.join(BUILD, "video.mp4"),
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const total = Math.ceil(timeline.duration * FPS);
  for (let f = 0; f < total; f++) {
    const buf = Buffer.from(await grab(f / FPS), "base64");
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % (FPS * 10) === 0) console.log(`${(f / FPS).toFixed(0)}s / ${timeline.duration.toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log(`done: build_${EP}/video.mp4`);
})();
