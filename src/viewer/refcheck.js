const { JSDOM } = require("jsdom"); const fs = require("fs"); const path = require("path");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" }); const w = dom.window, d = w.document;
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const seen = new Set();
const grab = () => d.querySelectorAll("m-model, m-audio").forEach((n) => { ["src", "anim"].forEach((k) => { const v = n.getAttribute(k); if (v) seen.add(v.split("?")[0].replace(/^https?:\/\/[^/]+\/[^/]+\/[^/]+\/[^/]+\//, "")); }); });
const obs = new w.MutationObserver(grab); obs.observe(d, { subtree: true, childList: true, attributes: true });
w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: 1 } }));
const host = d.getElementById("sp-host"); const say = (c) => fire(host, "prompt", { value: "7747 " + c, connectionId: 9 });
say("build"); say("hall open");
// click everything clickable once
d.querySelectorAll("m-cube, m-model").forEach((n) => fire(n, "click", { connectionId: 1 }));
setTimeout(() => { grab();
  const missing = [...seen].filter((f) => !fs.existsSync(path.join(process.argv[3], f)));
  console.log("referenced", seen.size, "missing", missing.length, missing.slice(0, 40)); process.exit(0); }, 6000);
