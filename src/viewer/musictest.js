const fire = (n, name, detail) => n.dispatchEvent(new window.CustomEvent(name, { detail, bubbles: true }));
const host = document.getElementById("sp-host"), board = document.getElementById("sp-remote");
const cmd = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 99 }); return (JSON.parse(board.getAttribute("data-ack") || "{}")).t; };
const n = () => Array.from(document.querySelectorAll("m-audio")).filter((a) => /radio_|jazz_|swamp_jazz/.test(a.getAttribute("src")));
(async () => {
  window.dispatchEvent(new CustomEvent("connected", { detail: { connectionId: 1 } })); cmd("remote"); cmd("build");
  await new Promise((r) => setTimeout(r, 800));
  const a = n(); console.log("speakers playing", a.length, "same start-time:", new Set(a.map((x) => x.getAttribute("start-time"))).size === 1, a[0] && a[0].getAttribute("src").split("/").pop());
  console.log(cmd("music next"), "->", n().length, n()[0] && n()[0].getAttribute("src").split("/").pop().split("?")[0]);
  console.log(cmd("music off"), "->", n().length); console.log(cmd("music on"), "->", n().length);
  const k = Array.from(document.querySelectorAll("m-model")).filter((m) => /sp_koda_/.test(m.getAttribute("src")));
  console.log("kodas", k.length, "animated", k.filter((m) => m.getAttribute("anim")).length);
  const fr = Array.from(document.querySelectorAll("m-model")).filter((m) => /sp_m_frog/.test(m.getAttribute("src")) && parseFloat(m.parentNode.parentNode.getAttribute("y") || "0") < 10);   // the lounge pond (not the escape choir)
  console.log("frogs", fr.length, "dragonflies", Array.from(document.querySelectorAll("m-model")).filter((m) => /dragonfly/.test(m.getAttribute("src"))).length);
  // click a frog
  const hb = fr[0].parentNode.parentNode.querySelector("m-cube");
  const before = Array.from(document.querySelectorAll("m-audio")).filter((x) => /frog_/.test(x.getAttribute("src"))).length;
  fire(hb, "click", { connectionId: 5 });
  const after = Array.from(document.querySelectorAll("m-audio")).filter((x) => /frog_/.test(x.getAttribute("src"))).length;
  console.log("frog click croaks:", after > before, "frog y anim:", !!fr[0].parentNode.querySelector("m-attr-anim[attr=y]"));
  window.__testDone = true;
})();
