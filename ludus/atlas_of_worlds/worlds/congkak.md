# Congkak

*mancala game*

`congkak` &nbsp; state: **DEEPENED** &nbsp; method: **heuristic**

## Found layer (recorded, not trusted)

| field | value |
| --- | --- |
| wikidata | Q473986 |
| wikipedia | Southeast Asian mancala |
| genres (source) | -- |
| instance of (source) | board game, mancala, solved game |
| country of origin | Indonesia |

## Declared layer (orders bench work)

| field | value |
| --- | --- |
| year created | -- |
| epoch | -- |
| region | SOUTHEAST_ASIA |
| media | MANCALA |
| players | 2 |
| age band | -- |
| exogenous process | NONE |
| loss shape | OPPORTUNITY_ONLY |
| live axes | COMMIT_BLIND |
| horizon | -- |
| scoring shape | SET_COLLECTION_CONVEX |
| information | SIMULTANEOUS |
| interaction | SOLITAIRE |
| turn structure | SIMULTANEOUS |
| tractability | EXACT |
| randomness | SIMULTANEOUS_CHOICE |
| luck factor | 0.05 |
| rules complexity | 2.2 |
| strategic depth | 1.4 |
| novelty | 0.8454 |
| solved status | SOLVED_STRONG |
| strategies | route_optimisation, set_collection |
| algorithms | -- |

## Object model

```
Episode
  players      : 2
  turn_structure: SIMULTANEOUS
  horizon       : ?
  scoring       : SET_COLLECTION_CONVEX

Pits           -- cyclic array of counts
Store          -- player's banked seeds
SealedChoice   -- irrevocable choice made without observation
```

## State transition diagram

```mermaid
stateDiagram-v2
    [*] --> Setup
    Setup --> Commit
    Commit --> Reveal : all players choose blind
    Reveal --> Resolve
    Resolve --> [*] : supply exhausted
```

## Research item -- turn trace

```
# Congkak -- simulated turn events
# generated from the DECLARED vector, not from a rulebook.
# structure: exo=NONE loss=OPPORTUNITY_ONLY horizon=None scoring=SET_COLLECTION_CONVEX axes=COMMIT_BLIND

t=0    SETUP        players=2  pot=0  capacity=7
t=1    FORCED       p1 single legal option taken (pot_gain=+1.2)
t=2    FORCED       p1 single legal option taken (pot_gain=+0.8)
t=3    FORCED       p1 single legal option taken (pot_gain=+1.5)
t=4    ENDTURN      turn passes to p2
t=5    FORCED       p2 single legal option taken (pot_gain=+1.5)
t=6    FORCED       p2 single legal option taken (pot_gain=+0.7)
t=7    FORCED       p2 single legal option taken (pot_gain=+0.9)
t=8    FORCED       p2 single legal option taken (pot_gain=+1.0)
t=9    FORCED       p2 single legal option taken (pot_gain=+1.2)
t=10   FORCED       p2 single legal option taken (pot_gain=+0.5)
t=11   ENDTURN      turn passes to p1
t=12   FORCED       p1 single legal option taken (pot_gain=+1.2)
t=13   FORCED       p1 single legal option taken (pot_gain=+1.2)
t=14   FORCED       p1 single legal option taken (pot_gain=+0.5)
t=15   FORCED       p1 single legal option taken (pot_gain=+0.8)
t=16   FORCED       p1 single legal option taken (pot_gain=+1.5)
t=17   FORCED       p1 single legal option taken (pot_gain=+1.4)
t=18   FORCED       p1 single legal option taken (pot_gain=+1.1)
t=19   FORCED       p1 single legal option taken (pot_gain=+1.1)
t=20   FORCED       p1 single legal option taken (pot_gain=+0.6)
t=21   FORCED       p1 single legal option taken (pot_gain=+1.5)
t=22   FORCED       p1 single legal option taken (pot_gain=+1.9)
t=23   ENDTURN      turn passes to p2
t=24   FORCED       p2 single legal option taken (pot_gain=+1.4)
t=25   FORCED       p2 single legal option taken (pot_gain=+1.7)
t=26   FORCED       p2 single legal option taken (pot_gain=+0.9)
t=27   ENDTURN      turn passes to p1

terminal: VARIABLE
```

## Conditions

| kind | threshold | effect | trigger |
| --- | --- | --- | --- |
| TERMINATE | -- | -- | The first round ends when a player has no more seeds in their holes. |
| BOUNDARY | -- | -- | Indonesia has the largest variation of Southeast Asian mancalas and thus may be likely to be at least one of the major entry points, though this may also be just an artifact of the country's size. |
| PENALTY | -- | -- | They forfeit their turn and stop playing. |
| PENALTY | -- | -- | If the seed drops into an empty hole belonging to the opponent: the player forfeits their turn and stops playing. |
| PENALTY | -- | -- | They also forfeit their seeds and leave it in the opponent's hole. |

## Source extract

Southeast Asian mancalas are a subtype of mancala games predominantly found in Southeast Asia.
They are known as congkak in Malaysia; congklak (VOS Spelling: tjongklak), congkak, congka, and
dakon in Indonesia and Brunei; sungkâ in the Philippines; and Makkhum หมากขุม or Maklum หมากหลุม
(Hole Game) in Thailand. They differ from other mancala games in that the player's store is
included in the placing of the seeds. Like other mancalas, they vary widely in terms of the
rules and number of holes used.   == Names ==  Southeast Asian mancalas are generally known by
variations of similar cognates which are likely onomatopoeiac. The names have also come to mean
the cowrie shells, predominantly used as the seeds of the game. These names include congkak in
Malaysia, congklak (VOS Spelling: tjongklak; also spelled as tsjongklak in Dutch sources),
congkak, congka, and jogklak in Indonesia, Brunei, and Singapore, and sungkâ (also spelled
chonca or chongca by Spanish sources) in the Philippines. Historical records show that similar
games also existed in Sri Lanka (where it is known as chonka) and India. In Tamil Nadu, India,
it is known as Pallanguzhi. A similar game is still found in the Maldi

<sub>Wikipedia, CC BY-SA. Retained as evidence for the structural
classification above. Every rule inferred from it is HYPOTHESIZED
until audited against a rulebook.</sub>
