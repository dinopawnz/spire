// run spire.html's script in a fake DOM and poke it like players + the remote would
const { JSDOM } = require("jsdom");
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");
const dom = new JSDOM(html, { runScripts: "dangerously" });
const w = dom.window, d = w.document;
const errs = []; w.addEventListener("error", (e) => errs.push(e.message));
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const board = d.getElementById("sp-remote"), host = d.getElementById("sp-host");
const ack = () => JSON.parse(board.getAttribute("data-ack") || "{}").t;
const cmd = (c, id = 99) => { fire(host, "prompt", { value: "7747 " + c, connectionId: id }); return ack(); };
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  for (const id of [1, 2, 3, 99]) w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: id } }));
  console.log("remote:", cmd("remote"));
  console.log("build:", cmd("build"));
  const all = d.querySelectorAll("*").length, models = d.querySelectorAll("m-model").length;
  console.log("elements", all, "models", models, "pads", d.querySelectorAll("m-cube[collide=true]").length, "zones", Object.keys(JSON.parse(board.getAttribute("data-game"))).length);
  // the probe: put player 1 in the hall, 2 at the bar, 3 by the lift
  const probe = d.querySelector("m-position-probe");
  const at = (id, x, y, z) => fire(probe, "positionmove", { connectionId: id, elementRelative: { position: { x, y, z } } });
  at(1, 3, 11, 13); at(2, -1, 3, -18); at(3, 11.6, 3, 4);
  const zoneGroups = Array.from(d.querySelectorAll("m-group[visible-to]")).map((g) => g.getAttribute("visible-to"));
  console.log("zone visible-to lists:", zoneGroups.slice(0, 8).join(" | "));
  // portraits
  const ports = Array.from(d.querySelectorAll("m-model")).filter((m) => /portraits\/pf_/.test(m.getAttribute("src")));
  console.log("hall portraits", ports.length);
  fire(ports[5], "click", { connectionId: 1 });              // before open -> NOT YET
  console.log("open:", cmd("hall open"));
  const realSrc = /pf_0821\.glb/; const real = ports.find((m) => realSrc.test(m.getAttribute("src")));
  const fake = ports.find((m) => !realSrc.test(m.getAttribute("src")));
  fire(fake, "click", { connectionId: 1 });
  fire(real, "click", { connectionId: 1 });                    // locked out, ignored
  fire(real, "click", { connectionId: 2 });                    // finalist
  console.log("after picks:", ack());
  console.log("thin:", cmd("hall thin")); await wait(3500);
  console.log("thin:", cmd("hall thin")); await wait(3500);
  const left = Array.from(d.querySelectorAll("m-model")).filter((m) => /portraits\/pf_/.test(m.getAttribute("src"))).length;
  console.log("hall portraits still in the scene", left);
  console.log("finals:", cmd("hall finals"));
  const vps = Array.from(d.querySelectorAll("m-model")).filter((m) => /portraits\/pv_/.test(m.getAttribute("src")));
  const vreal = vps.find((m) => /pv_063\.glb/.test(m.getAttribute("src")));
  fire(vreal, "click", { connectionId: 3 });                   // not a finalist
  fire(vreal, "click", { connectionId: 2 });                   // wins
  console.log("after vault:", ack());
  // taps + NPC + guest book
  const tapHits = Array.from(d.querySelectorAll("m-model")).filter((m) => /sp_tap\.glb/.test(m.getAttribute("src"))).map((m) => m.parentNode.querySelector("m-cube"));
  fire(tapHits[0], "click", { connectionId: 2 }); await wait(2700);
  console.log("mugs on the bar", Array.from(d.querySelectorAll("m-model")).filter((m) => /sp_mug/.test(m.getAttribute("src"))).length);
  const book = d.querySelector("m-prompt:not(#sp-host)"); fire(book, "prompt", { connectionId: 2, value: "Dino" }); console.log("book:", ack());
  const npcHit = Array.from(d.querySelectorAll("m-model")).filter((m) => /npc_gator\.glb/.test(m.getAttribute("src")))[0].parentNode.querySelector("m-cube");
  fire(npcHit, "click", { connectionId: 2 });
  console.log("bubbles now", Array.from(d.querySelectorAll("m-model")).filter((m) => /\/sb_/.test(m.getAttribute("src"))).map((m) => m.getAttribute("src").split("/").pop()));
  // lifts: call A to the gallery, B to the deck
  console.log(cmd("lift A gallery")); console.log(cmd("lift B roof"));
  await wait(1500);
  const g = JSON.parse(board.getAttribute("data-game")); console.log("lifts", JSON.stringify(g.lifts));
  await wait(16000);
  console.log("lifts later", JSON.stringify(JSON.parse(board.getAttribute("data-game")).lifts));
  console.log("players", board.getAttribute("data-players"));
  console.log("lite:", cmd("lite")); console.log("refresh:", cmd("refresh")); console.log("unbuild:", cmd("unbuild")); console.log("build again:", cmd("build"));
  console.log("ERRORS:", errs.length ? errs : "none");
  process.exit(0);
})();
