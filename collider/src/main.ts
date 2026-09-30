import "./styles.css";
import { DataStore } from "./data/store";
import { App } from "./ui/app";

async function boot() {
  const store = new DataStore();
  await store.load();
  if (!store.loaded.concepts) {
    document.body.insertAdjacentHTML("beforeend", `<div style="position:fixed;inset:0;display:grid;place-items:center;font-family:monospace;color:#aaa">concept dictionary missing: run \`npm run ingest\`</div>`);
    return;
  }
  const app = new App(store);
  app.start();
  (window as any).__collider = app;
}

boot();
