const fire = (n, name, detail) => n.dispatchEvent(new window.CustomEvent(name, { detail, bubbles: true }));
const host = document.getElementById("sp-host"), board = document.getElementById("sp-remote");
const cmd = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 99 }); return (JSON.parse(board.getAttribute("data-ack") || "{}")).t; };
(async () => {
  window.dispatchEvent(new CustomEvent("connected", { detail: { connectionId: 1 } })); cmd("remote"); cmd("build");
  await new Promise((r) => setTimeout(r, 600));
  const balls = Array.from(document.querySelectorAll("m-model")).filter((m) => /sp_ball_/.test(m.getAttribute("src")));
  console.log("balls", balls.length, "tables", Array.from(document.querySelectorAll("m-model")).filter((m) => /pooltable/.test(m.getAttribute("src"))).length);
  const imgs = Array.from(document.querySelectorAll("m-image")).filter((m) => /pool_btn_hard/.test(m.getAttribute("src")));
  const hard = imgs[0].parentNode.querySelector("m-cube");
  const pos0 = balls.slice(0, 16).map((b) => [b.parentNode.getAttribute("x"), b.parentNode.getAttribute("z")].join(","));
  window.onerror = (m) => console.log("ERR", m);
  try { fire(hard, "click", { connectionId: 7 }); } catch (e) { console.log("EXC", e.message); }
  await new Promise((r) => setTimeout(r, 700));
  console.log("after 0.7s: ball anims", Array.from(document.querySelectorAll("m-attr-anim")).filter((a) => a.parentNode && a.parentNode.parentNode && /sp_ball_/.test((a.parentNode.querySelector("m-model") || {}).getAttribute ? a.parentNode.querySelector("m-model").getAttribute("src") : "")).length, "hard btn img count", imgs.length);
  await new Promise((r) => setTimeout(r, 9000));
  const pos1 = balls.slice(0, 16).map((b) => [b.parentNode.getAttribute("x"), b.parentNode.getAttribute("z"), b.parentNode.getAttribute("visible")].join(","));
  console.log("moved", pos1.filter((p, i) => p.split(",").slice(0, 2).join(",") !== pos0[i]).length, "of 16; pocketed", pos1.filter((p) => p.endsWith("false")).length);
  console.log("anims made", document.querySelectorAll("m-attr-anim").length, "sounds", Array.from(document.querySelectorAll("m-audio")).filter((a) => /pool_/.test(a.getAttribute("src"))).length);
  console.log(cmd("pool"));
  // drums: each piece its own sound
  const ds = new Set(); Array.from(document.querySelectorAll("m-cube")).forEach(() => {});
  window.__testDone = true;
})();
