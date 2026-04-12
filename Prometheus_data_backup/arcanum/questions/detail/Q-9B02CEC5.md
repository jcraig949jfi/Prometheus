# Q-9B02CEC5

> How collapse distance in self-similar tensor foliated hypersurfaces?

**Author:** GROK | **Top Score:** 0.3061 | **Top Machine:** gandalf | **Top Model:** Qwen2.5-0.5B-Instruct

[← Back to DiscoveryDB](../DiscoveryDB.md)

## Screening Run History

| Machine | Model | Score | Layer | Timestamp | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| gandalf | Qwen2.5-0.5B-Instruct | 0.3061 | 20 | 2026-03-20T21:42:50 | ✅ CAPTURE |
| gandalf | Qwen2.5-0.5B-Instruct | 0.2503 | 18 | 2026-03-20T19:08:51 | ✅ CAPTURE |
| skullport | Qwen2.5-1.5B-Instruct | 0.0760 | 21 | 2026-03-20T11:46:35 | ✅ HIT |
| skullport | Qwen2.5-1.5B-Instruct | 0.0706 | 15 | 2026-03-20T12:29:23 | ✅ HIT |

---

## 🔒 Expert Analysis

<!-- [SAFE] -->
**Prompt:** "How collapse distance in self-similar tensor foliated hypersurfaces?"

**Finding:** All four runs are HITs or CAPTUREs. 0.5B: 0.3061 at layer 20, 0.2503 at layer 18. 1.5B: 0.0760, 0.0706 at layers 21 and 15. The 0.5B captured at layer **20** on its best run — deeper than the usual layer 18, and a CAPTURE rather than HIT.

**Interpretation:** The question is syntactically broken — "How [does] collapse distance [behave] in..." is missing words. Like Q-7C8DDBD8, syntactic ambiguity appears to be a contributing factor. "Self-similar tensor foliated hypersurfaces" is a plausible-sounding invented compound — foliations are real (families of submanifolds), self-similarity is real (fractals), but their combination with "tensor foliated" is not a standard concept. The deeper layer-20 capture on 0.5B vs. the usual layer-18 suggests the model partially stabilizes before failing — it processes more of the question before collapsing.

**Signal:** Second example of a syntactically broken prompt in the high-score tier (alongside Q-7C8DDBD8). Cross-model destabilization confirmed. The broken grammar + invented compound pattern may be deliberately designed — worth checking with the GROK author.

**Analyst:** Claude Sonnet 4.6 | **Date:** 2026-03-21
<!-- [/SAFE] -->

