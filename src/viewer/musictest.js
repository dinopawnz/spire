const fire = (n, name, detail) => n.dispatchEvent(new window.CustomEvent(name, { detail, bubbles: true }));
const host = document.getElementById("sp-host"), board = document.getElementById("sp-remote");
const cmd = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 99 }); return (JSON.parse(board.getAttribute("data-ack") || "{}")).t; };
const n = () => Array.from(document.querySelectorAll("m-audio")).filter((a) => /swamp_jazz/.test(a.getAttribute("src")));
(async () => {
  window.dispatchEvent(new CustomEvent("connected", { detail: { connectionId: 1 } })); cmd("remote"); cmd("build");
  await new Promise((r) => setTimeout(r, 800));
  const a = n(); console.log("speakers playing", a.length, "same start-time:", new Set(a.map((x) => x.getAttribute("start-time"))).size === 1, a[0] && a[0].getAttribute("src").split("/").pop());
  console.log(cmd("music off"), "->", n().length); console.log(cmd("music on"), "->", n().length);
  window.__testDone = true;
})();
