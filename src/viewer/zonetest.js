const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" }); const w = dom.window, d = w.document;
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const host = d.getElementById("sp-host");
const cmd = (c) => fire(host, "prompt", { value: "7747 " + c, connectionId: 99 });
const zones = () => Array.from(d.querySelectorAll("m-group[visible-to]")).map((g) => [g.children.length, g.getAttribute("visible-to")]).filter((z) => z[0] > 3);
(async () => {
  w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: 1 } }));
  cmd("remote"); cmd("build");
  await new Promise((r) => setTimeout(r, 7000));
  console.log("after build, before any position:", JSON.stringify(zones()));
  const probe = d.querySelector("m-position-probe");
  fire(probe, "positionmove", { connectionId: 1, elementRelative: { position: { x: 5, y: 3.2, z: 10 } } });
  console.log("after position in lounge:", JSON.stringify(zones()));
  (window.__testDone = true);
})();
