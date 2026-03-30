# Task 4: Historical Transmission and Independent Invention

## 4A: The Transmission Chain

### Babylonian Reciprocal Tables (~2000 BCE)

Well-documented. Regular numbers (5-smooth) have finite sexagesimal reciprocals. Division reduced to multiplication-by-reciprocal using pre-computed tables. Old Babylonian period (c. 2000-1600 BCE) is the peak of mathematical table-text production.

### Babylon -> Greece (Documented but Debated)

**Friberg (2007)**, *Amazing Traces of a Babylonian Origin in Greek Mathematics* (World Scientific): Argues that Euclid's Book II geometric algebra is a "direct translation into non-metric and non-numerical 'geometric algebra' of key results from Babylonian metric algebra."

**Neugebauer (1988):** Found direct evidence of Babylonian astronomical methods in Greek papyri. The transmission path: Babylon -> Persia -> Hellenistic Egypt -> Greece.

**The Antikythera mechanism** uses Babylonian eclipse cycles (Saros cycle), demonstrating knowledge transfer of computational methods.

**Assessment:** The transmission of *mathematical content* from Babylon to Greece is well-established. Whether the *TDC structural pattern* was transmitted (as opposed to specific results) is less clear.

### Islamic Algebra: Al-Khwarizmi (~813-833 CE)

**Is al-jabr a TDC?** This is a defensible novel claim.

Al-Khwarizmi's al-jabr ("restoration/completion") is a *transformation* of equations into standard form:
1. Start with an equation in arbitrary form
2. Apply al-jabr (add terms to both sides to eliminate negatives) and al-muqabala (cancel like terms)
3. Arrive at one of six canonical forms
4. Apply the known solution procedure for that canonical form

This IS structurally a transform: DUALIZE (put in canonical form) -> MAP (apply known solution) -> INVERT (interpret result in original context).

Al-Khwarizmi explicitly drew on both Babylonian and Greek sources. His innovation was making the transformation procedure itself algorithmic and general.

**Assessment:** Calling al-jabr a TDC is novel but well-supported.

### Prosthaphaeresis (1580s) -- Critical Missing Link

Before logarithms, astronomers used trigonometric identities to convert multiplication to addition:

**cos(A) . cos(B) = [cos(A-B) + cos(A+B)] / 2**

Developed by Johannes Werner (c.1510), rediscovered by Tycho Brahe and Paul Wittich (1580s). This is **TDC with trigonometric functions as the transform domain.**

Napier explicitly knew of prosthaphaeresis and his logarithms generalize the principle. The product-to-sum idea was rediscovered within a single generation -- evidence for convergent evolution.

### Napier's Logarithms (1614)

Published *Mirifici Logarithmorum Canonis Descriptio*. Explicitly motivated by desire to simplify astronomical and navigational calculations. Drew on prosthaphaeresis tradition. ~20 years computing tables.

**The TDC structure is explicit in Napier's own description:** transform numbers to their logarithms, perform addition (easy), transform back via antilogarithm table.

### Burgi's Logarithms (1620)

*Arithmetische und Geometrische Progress-Tabulen*. Independently developed by 1588, published 1620. Based on correspondence between arithmetic and geometric progressions.

**Two independent inventions within ~6 years. Strongest evidence for TDC convergent evolution.**

### Euler's Exponential-Trigonometric Connection (1748)

Published in *Introductio in analysin infinitorum*. The formula e^(ix) = cos(x) + i sin(x) is **the theoretical bridge between logarithmic and Fourier TDC.** It shows exponentials (logarithmic domain) and trigonometric functions (Fourier domain) are the same operation in different domains.

This is the keystone: Euler unified the two TDC traditions (multiplicative via logarithms, vibrational via trigonometry) into a single framework.

### Fourier's Heat Equation (1807)

Decomposition of arbitrary functions into trigonometric series. Extends Euler's connection into a general computational framework. The key innovation is **completeness** -- any reasonable function can be represented in the transform domain.

### Gauss's FFT (~1805) -- A Rediscovery

**Critical:** Gauss used the FFT algorithm ~1805 for asteroid trajectory interpolation, published posthumously in Latin. Cooley-Tukey (1965) independently rediscovered it and demonstrated O(N log N) complexity.

**The FFT was independently invented at least twice (Gauss, Cooley-Tukey), plus various limited rediscoveries in between.**

### Assessment: Continuous Evolution or Independent Reinvention?

**Both, depending on the link:**
- Babylon -> Greece -> Islam -> Europe: plausible transmission chain for mathematical content
- Napier / Burgi: clearly independent reinvention
- Gauss / Cooley-Tukey: independent rediscovery (160-year gap)
- Prosthaphaeresis -> Napier: direct influence, same principle generalized

**The paper's argument:** This is precisely the point. The TDC *pattern* is so fundamental that it gets reinvented even when transmission fails. The structural operation is discovered independently because the PROBLEM (simplify a hard operation by transforming to a domain where it's easy) forces the SOLUTION regardless of cultural context.

---

## 4B: Independent Inventions Summary

### Logarithms
- **Napier (1614):** Scotland. Published *Mirifici Logarithmorum Canonis Descriptio*.
- **Burgi (c.1588-1620):** Switzerland/Prague. Independent development, published *Progress Tabulen*.
- **Kerala school:** Did NOT develop logarithms. Developed series expansions for trig functions and proto-calculus, but "the notion of a function, or of exponential or logarithmic functions, was not yet formulated" (Wikipedia). This is a gap in the convergent-invention narrative for logarithms specifically.

### The FFT
- **Gauss (~1805):** Developed for asteroid trajectory interpolation. Published posthumously.
- **Cooley & Tukey (1965):** Independent rediscovery. Published in *Mathematics of Computation*.

### Convergent Evolution Score
- Logarithms: 2 independent inventions (Napier, Burgi) + prosthaphaeresis as precursor
- FFT: 2 independent inventions (Gauss, Cooley-Tukey)
- Reciprocal tables: universal across base-60 mathematical traditions
- The product-to-sum principle: prosthaphaeresis (1580s), logarithms (1614), Fourier convolution theorem (1807)

---

## 4C: The Slide Rule as Physical TDC Device

### The Device (c.1620, Oughtred and others)

The slide rule physically instantiates logarithmic TDC:
1. **Input:** Numbers on the scales (multiplication domain)
2. **Transform:** Physical spacing IS the logarithm (the scale markings are logarithmically spaced)
3. **Compose:** Physical juxtaposition (addition of lengths = addition of logs = multiplication of numbers)
4. **Read output:** Transform back by reading the result scale

### Structural Parallels

| Device | Transform Domain | Physical Mechanism | Era |
|--------|-----------------|-------------------|-----|
| Babylonian clay tablet | Reciprocal domain | Table lookup | ~2000 BCE |
| Slide rule | Logarithmic domain | Spatial addition | ~1620 CE |
| Antikythera mechanism | Gear-ratio domain | Mechanical computation | ~100 BCE |
| Computer (FFT) | Frequency domain | Digital algorithm | 1965 CE |

### Has Anyone Connected These?

**No.** The slide rule and Antikythera mechanism are categorized together as early analog computers in general histories, but nobody draws the specific line: "Babylonian reciprocal table -> slide rule -> FFT as instances of the same pattern."

The Antikythera mechanism uses Babylonian eclipse cycles and gear-ratio computation (kinematic TDC). Connecting it to logarithmic TDC requires arguing gear-ratio computation is also a form of domain transformation. Defensible but needs careful argument.

### Strength Assessment
**MODERATE** -- The individual comparisons are straightforward; the unified framing is novel.

---

## Key Citations for This Section

- Friberg, J. (2007). *Amazing Traces of a Babylonian Origin in Greek Mathematics*. World Scientific.
- Neugebauer, O. (1988). Various papers on Babylonian astronomy transmission.
- Al-Khwarizmi -- MacTutor biography. Britannica: Islamic contributions to algebra.
- Napier -- MAA Convergence: "Logarithms: The Early History of a Familiar Function."
- Prosthaphaeresis -- Wikipedia.
- Heil, M. "Gauss and the History of the Fast Fourier Transform" (PDF).
- Slide rule -- Wikipedia.
