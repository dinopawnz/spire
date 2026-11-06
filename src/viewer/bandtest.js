const fire = (n, name, detail) => n.dispatchEvent(new window.CustomEvent(name, { detail, bubbles: true }));
const host = document.getElementById("sp-host"), board = document.getElementById("sp-remote");
const cmd = (c) => { fire(host, "prompt", { value: "7747 " + c, connectionId: 99 }); return (JSON.parse(board.getAttribute("data-ack") || "{}")).t; };
(async () => {
  window.dispatchEvent(new CustomEvent("connected", { detail: { connectionId: 1 } })); cmd("remote"); cmd("build");
  await new Promise((r) => setTimeout(r, 1500));
  const audios = () => Array.from(document.querySelectorAll("m-audio")).filter((a) => /band_|piano_|harp_/.test(a.getAttribute("src"))).map((a) => a.getAttribute("src").split("/").pop().split("?")[0]);
  const keys = Array.from(document.querySelectorAll("m-cube[collide=true]")).filter((c) => c.getAttribute("height") === "0.03");
  const hits = Array.from(document.querySelectorAll("m-cube")).filter((c) => c.getAttribute("collide") === "false" && c.getAttribute("opacity") === "0");
  console.log("piano keys", keys.length, "clickable zones", hits.length);
  fire(keys[0], "click", { connectionId: 1 }); await new Promise((r) => setTimeout(r, 120)); fire(keys[20], "click", { connectionId: 1 });
  console.log("after 2 keys:", audios().join(" "));
  console.log(cmd("instruments off")); fire(keys[5], "click", { connectionId: 2 }); console.log("off, click ->", audios().length, "sounds (should stay 2)");
  console.log(cmd("instruments on"));
  window.__testDone = true;
})();
