const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" });
const w = dom.window, d = w.document; const errs = []; w.addEventListener("error", (e) => errs.push(e.message));
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const host = d.getElementById("sp-host"), board = d.getElementById("sp-remote");
const cmd = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 99 }); return JSON.parse(board.getAttribute("data-ack") || "{}").t; };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  for (const id of [1, 2, 99]) w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: id } }));
  cmd("remote"); console.log(cmd("build"));
  console.log("bio images", d.querySelectorAll("m-image").length, "spores", d.querySelectorAll("m-sphere").length);
  const probe = d.querySelector("m-position-probe");
  const at = (id, x, y, z) => fire(probe, "positionmove", { connectionId: id, elementRelative: { position: { x, y, z } } });
  // player 1 walks the lounge, player 2 walks the front run of the winding stair (y on the ramp ~14)
  for (let k = 0; k < 8; k++) { at(1, -10 + k * 2, 3.0, 12); at(2, 28 - k * 2.2, 13.7 + 0.03 * k, 27.6); await wait(700); }
  console.log("ring ys", Array.from(d.querySelectorAll("m-image")).filter((m) => /bio_ring/.test(m.getAttribute("src"))).map((m) => m.getAttribute("y") + "@" + m.getAttribute("x")).join(" "));
  console.log("rings now", Array.from(d.querySelectorAll("m-image")).filter((m) => /bio_ring/.test(m.getAttribute("src"))).length,
              "sheens now", Array.from(d.querySelectorAll("m-image")).filter((m) => /bio_sheen/.test(m.getAttribute("src"))).length);
  const r = Array.from(d.querySelectorAll("m-image")).find((m) => /bio_ring/.test(m.getAttribute("src"))); console.log("a ring at y", r && r.getAttribute("y"));
  await wait(2000);
  console.log("after", Array.from(d.querySelectorAll("m-image")).filter((m) => /bio_ring|bio_sheen/.test(m.getAttribute("src"))).length);
  console.log("lite:", cmd("lite"), "images left", d.querySelectorAll("m-image").length);
  console.log("ERRORS:", errs.length ? errs : "none"); process.exit(0);
})();
