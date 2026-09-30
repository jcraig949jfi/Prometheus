// Shareable, replayable collision addresses (hash-based so any static host works).
//   #h=<historical-id>                                  a historical Hephaestus triple
//   #n=A|B|C&s=<seed>&src=<kind>[&p=<parent>&m=<mut>]    anything else, order preserved

import type { SourceKind } from "./types";

export interface CollisionAddress {
  historicalId?: string;
  names?: [string, string, string];
  seed?: number;
  source?: SourceKind;
  parent?: string;
  mutation?: string;
  archetype?: string;
}

export function encodeAddress(a: CollisionAddress): string {
  const p = new URLSearchParams();
  if (a.historicalId) p.set("h", a.historicalId);
  else if (a.names) {
    p.set("n", a.names.join("|"));
    p.set("s", String(a.seed ?? 0));
    if (a.source) p.set("src", a.source);
  }
  if (a.parent) p.set("p", a.parent);
  if (a.mutation) p.set("m", a.mutation);
  if (a.archetype) p.set("a", a.archetype);
  return "#" + p.toString();
}

export function decodeAddress(hash: string): CollisionAddress | null {
  const s = hash.replace(/^#/, "");
  if (!s) return null;
  const p = new URLSearchParams(s);
  if (p.get("h")) return { historicalId: p.get("h")!, parent: p.get("p") ?? undefined, mutation: p.get("m") ?? undefined };
  const n = p.get("n");
  if (!n) return null;
  const names = n.split("|").map((x) => x.trim()).filter(Boolean);
  if (names.length !== 3) return null;
  const seed = Number(p.get("s") ?? "0");
  const src = (p.get("src") as SourceKind | null) ?? "user";
  return {
    names: names as [string, string, string],
    seed: Number.isFinite(seed) ? seed >>> 0 : 0,
    source: src,
    parent: p.get("p") ?? undefined,
    mutation: p.get("m") ?? undefined,
    archetype: p.get("a") ?? undefined,
  };
}
