const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" }); const w = dom.window, d = w.document;
const errs = []; w.addEventListener("error", (e) => errs.push(e.message));
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const host = d.getElementById("sp-host"); const say = (c) => fire(host, "prompt", { value: "7747 " + c, connectionId: 9 });
const mugs = () => Array.from(d.querySelectorAll("m-model")).filter((m) => /sp_mug/.test(m.getAttribute("src")));
(async () => {
  for (const id of [1, 2, 9]) w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: id } }));
  say("remote"); say("build");
  const tap = Array.from(d.querySelectorAll("m-model")).find((m) => /sp_tap\.glb/.test(m.getAttribute("src"))).parentNode.querySelector("m-cube");
  fire(tap, "click", { connectionId: 1 }); await new Promise((r) => setTimeout(r, 2800));
  const mug = mugs()[0].parentNode, hit = mug.querySelector("m-cube");
  console.log("mugs on bar", mugs().length);
  fire(hit, "click", { connectionId: 2 }); await new Promise((r) => setTimeout(r, 200)); console.log("someone else clicks -> still there:", mugs().length);
  fire(hit, "click", { connectionId: 1 }); await new Promise((r) => setTimeout(r, 2600)); console.log("owner drinks -> mugs left:", mugs().length);
  console.log("gulp played:", d.querySelectorAll("m-audio[src*=gulp]").length > 0 || "already finished", "ERRORS:", errs.length ? errs : "none"); process.exit(0);
})();
