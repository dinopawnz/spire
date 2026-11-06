// local MML document server (networked-dom) for testing spire.html + spire_remote.html together
import { EditableNetworkedDOM, LocalObservableDOMFactory } from "@mml-io/networked-dom-server";
import { WebSocketServer } from "ws";
import fs from "fs";
const file = process.argv[2], port = +process.argv[3] || 7079;
const doc = new EditableNetworkedDOM("file://" + file, LocalObservableDOMFactory, true, (m) => console.log("[doc]", m.level, JSON.stringify(m.content).slice(0, 300)));
doc.load(fs.readFileSync(file, "utf8"));
const wss = new WebSocketServer({ port, handleProtocols: (ps) => (ps.has("networked-dom-v0.1") ? "networked-dom-v0.1" : [...ps][0]) });
wss.on("connection", (ws) => { doc.addWebSocket(ws); ws.on("close", () => doc.removeWebSocket(ws)); });
console.log("serving", file, "on ws://localhost:" + port);
