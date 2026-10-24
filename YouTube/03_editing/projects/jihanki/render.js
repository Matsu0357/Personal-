// render.html を Playwright で1コマずつ描いて、ffmpeg で動画にする。
// 使い方:
//   node render.js                 → build/video.mp4（音声付き）
//   node render.js --preview 5,30  → build/preview_5.jpg などの確認用画像
//   node render.js --thumb         → build/thumbnail_black.png / thumbnail_red.png
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

const FPS = 30;
const BUILD = path.join(__dirname, "build");

(async () => {
  const timeline = JSON.parse(fs.readFileSync(path.join(BUILD, "timeline.json"), "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  await page.goto("file://" + path.join(__dirname, "render.html"));
  await page.evaluate(tl => window.init(tl), timeline);

  const grab = t => page.evaluate(t => {
    window.renderFrame(t);
    return document.getElementById("c").toDataURL("image/jpeg", 0.92).split(",")[1];
  }, t);

  if (process.argv.includes("--thumb")) {
    for (const v of ["black", "red"]) {
      await page.evaluate(v => window.renderThumb(v), v);
      const png = await page.evaluate(() => document.getElementById("c").toDataURL("image/png").split(",")[1]);
      fs.writeFileSync(path.join(BUILD, `thumbnail_${v}.png`), Buffer.from(png, "base64"));
    }
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
    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
    path.join(BUILD, "video.mp4"),
  ], { stdio: ["pipe", "inherit", "inherit"] });

  const total = Math.ceil(timeline.duration * FPS);
  for (let f = 0; f < total; f++) {
    const buf = Buffer.from(await grab(f / FPS), "base64");
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (f % (FPS * 20) === 0) console.log(`${(f / FPS).toFixed(0)}s / ${timeline.duration.toFixed(0)}s`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
  await browser.close();
  console.log("done: build/video.mp4");
})();
