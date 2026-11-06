const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" });
const w = dom.window, d = w.document;
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const host = d.getElementById("sp-host");
const cmd = (c) => fire(host, "prompt", { value: "7747 " + c, connectionId: 99 });
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  for (const id of [2, 99]) w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: id } }));
  cmd("remote"); cmd("build");
  const probe = d.querySelector("m-position-probe");
  const obs = new w.MutationObserver((ms) => ms.forEach((m) => m.addedNodes.forEach((n) => { if (n.getAttribute && /bio_sheen/.test(n.getAttribute("src") || "")) console.log("SHEEN", n.getAttribute("x"), n.getAttribute("y"), n.getAttribute("z")); })));
  obs.observe(d, { subtree: true, childList: true });
  for (let k = 0; k < 6; k++) { fire(probe, "positionmove", { connectionId: 2, elementRelative: { position: { x: 28 - k * 2.2, y: 13.75, z: 27.6 } } }); await wait(700); }
  process.exit(0);
})();
