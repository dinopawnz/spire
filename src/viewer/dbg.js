const { JSDOM } = require("jsdom"); const fs = require("fs");
const dom = new JSDOM(fs.readFileSync(process.argv[2], "utf8"), { runScripts: "dangerously" }); const w = dom.window, d = w.document;
const fire = (n, name, detail) => n.dispatchEvent(new w.CustomEvent(name, { detail, bubbles: true }));
w.dispatchEvent(new w.CustomEvent("connected", { detail: { connectionId: 99 } }));
fire(d.getElementById("sp-host"), "prompt", { value: "7747 remote", connectionId: 99 });
fire(d.getElementById("sp-host"), "prompt", { value: "7747 build", connectionId: 99 });
console.log(JSON.parse(d.getElementById("sp-remote").getAttribute("data-ack")).l.map((x) => x.t).join("\n")); process.exit(0);
