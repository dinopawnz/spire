const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" }); const w = dom.window, d = w.document;
const errs = []; w.addEventListener("error", (e) => errs.push(e.message));
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
const host = d.getElementById("sp-host"), board = d.getElementById("sp-remote");
const say = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 9 }); return JSON.parse(board.getAttribute("data-ack")).t; };
const bubbles = (who) => Array.from(d.querySelectorAll("m-model")).filter((m) => new RegExp("/sb_" + who + "_").test(m.getAttribute("src"))).map((m) => m.getAttribute("src").split("/").pop().split("?")[0]);
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
(async () => {
  for (const id of [1, 2, 9]) w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: id } }));
  say("remote"); say("build");
  const gHit = Array.from(d.querySelectorAll("m-model")).find((m) => /npc_gator\.glb/.test(m.getAttribute("src"))).parentNode.querySelector("m-cube");
  for (let i = 0; i < 10; i++) fire(gHit, "click", { connectionId: 1 + (i % 2) });         // spam
  console.log("spam 10 clicks -> gator bubbles:", bubbles("gator"));
  await wait(9000); fire(gHit, "click", { connectionId: 1 }); console.log("after he finished, click -> ", bubbles("gator"));
  console.log(say("npc mode host")); await wait(9000); fire(gHit, "click", { connectionId: 1 }); console.log("host mode click ->", bubbles("gator"));
  console.log(say("npc say gator t4")); console.log("host line ->", bubbles("gator"));
  console.log(say("npc say gator t5")); console.log("host line cuts in ->", bubbles("gator"));
  console.log(say("npc mode off")); console.log(say("lift A hall")); await wait(3000); console.log("off mode, lift moving -> operator bubbles:", bubbles("operator"));
  console.log(say("npc say operator greet")); console.log("host line in off mode ->", bubbles("operator"));
  console.log(say("npc hush")); console.log("after hush ->", bubbles("operator"), bubbles("gator"));
  console.log(say("npc mode on"));
  const music = () => d.querySelectorAll("m-audio[src*=lift_music]").length;
  console.log("music players", music(), say("liftmusic off"), music(), say("liftmusic on"), music());
  console.log("game npcMode", JSON.parse(board.getAttribute("data-game")).npcMode);
  console.log("ERRORS:", errs.length ? errs : "none"); process.exit(0);
})();
