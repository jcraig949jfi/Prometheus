| cell | wave | topo/update | env | lc bound | C1 held | C1 relay_pv32 | P-FLIP base (M64) | refresh M32 (OVR L22) | thin M16 (OVR L28) | physics tags | class (reading) | FLIP_FEEDBACK |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 996716ac46f73a43 | A | torus sync | d1 dl8 b4 | 1.00 | 0.532 | 0.562 | exact 1.000 [1.000,1.000] | 1.000 | nan | cap4alo econ | **PLANT-SOLVED** base exact 1.000 [1.000,1.000] M64 | PASS (conservative diff >= 0.50; teachers-removed 0.500) |
| 6f82f9c7d51bcef1 | C | ring sync | d3 dl16 b4 | 1.00 | 0.479 | 0.573 | exact 0.943 [0.888,0.984] | 0.943 | nan | cap2sat | **PLANT-SOLVED** base exact 0.943 [0.888,0.984] M64 | PASS (paired diff lo99 .359; teachers-removed .516) |
| 64d33b89811637f7 | A | torus async | d1 dl8 b2 | 1.00 | 0.513 | 0.500 | exact 0.854 [0.785,0.916] | 0.852 | nan | cap2alo async0.8 econ | **PLANT-SOLVED** base exact 0.854 [0.785,0.916] M64 | PASS (conservative diff >= 0.25; teachers-removed 0.504) |
| f476a3cac974379b | A | global async | d1 dl4 b2 | 1.00 | 0.498 | 0.477 | exact 0.563 [0.509,0.624] | 0.521 | 0.539 | loss0.3 async0.5 global econ | **UNDECIDED** best base 0.563 | - |
| ec89b3d5b8bd2a31 | A | global async | d3 dl4 b2 | 1.00 | 0.492 | 0.480 | exact 0.550 [0.486,0.618] | 0.543 | 0.508 | decay6 loss0.3 async0.8 global | **UNDECIDED** best base 0.550 | - |
| 50060cf95d2b41ae | A | random async | d2 dl8 b2 | 1.00 | 0.497 | 0.504 | exact 0.529 [0.458,0.602] | 0.566 | 0.566 | async0.5 econ | **UNDECIDED** best refresh 0.566 | - |
| 07bde99b2b98a3bc | A | global sync | d2 dl8 b4 | 1.00 | 0.493 | 0.526 | OVR L8->16 0.522 [0.465,0.586] | 0.518 | 0.521 | loss0.3 global econ | **UNDECIDED** best base 0.522 | - |
| bfa85a55ee67f7fb | A | smallworld sync | d1 dl4 b4 | 1.00 | 0.503 | 0.521 | OVR L12->16 0.521 [0.456,0.589] | 0.615 | 0.729 | decay3 cap1sat | **R-CANDIDATE** thin OVR 0.719 [0.661,0.773] M64 | PASS (paired diff lo99 0.112) |
| 5fbaa2ecc6981966 | A | global sync | d1 dl16 b2 | 1.00 | 0.500 | 0.516 | OVR L8->16 0.520 [0.452,0.595] | 0.586 | 0.531 | decay6 cap1sat loss0.3 global econ | **UNDECIDED** best refresh 0.586 | - |
| a467c0f81468bc01 | A | ring async | d3 dl8 b2 | 1.00 | 0.490 | 0.438 | exact 0.515 [0.450,0.573] | 0.521 | 0.500 | async0.5 | **UNDECIDED** best refresh 0.521 | - |
| a4d9f2e4c636234e | A | smallworld sync | d1 dl16 b2 | 1.00 | 0.492 | 0.500 | exact 0.514 [0.480,0.547] | 0.633 | nan | decay3 cap4alo loss0.6 | **R-CANDIDATE** refresh OVR 0.645 [0.586,0.701] M64 | FAIL (paired diff lo99 0.049) |
| 9d67b56354697956 | A | random sync | d5 dl16 b4 | 1.00 | 0.502 | 0.526 | OVR L12->16 0.513 [0.471,0.561] | 0.516 | 0.500 | decay6 loss0.6 econ | **UNDECIDED** best refresh 0.516 | - |
| f3e99f332406b1d3 | C | global sync | d2 dl8 b4 | 1.00 | 0.498 | 0.471 | exact 0.513 [0.497,0.529] | 0.495 | 0.510 | decay6 global econ | **UNDECIDED** best base 0.513 | - |
| 158bdd9a126414e5 | C | global async | d5 dl16 b4 | 1.00 | 0.501 | 0.500 | OVR L8->16 0.512 [0.488,0.538] | 0.875 | nan | decay3 async0.8 global | **R-CANDIDATE** refresh OVR 0.875 [0.802,0.938] M32 | PASS (conservative diff >= 0.30; teachers-removed 0.479, M32) |
| e0c6650c66aaf2d1 | A | ring async | d2 dl4 b2 | 1.00 | 0.501 | 0.500 | exact 0.511 [0.433,0.600] | 0.482 | 0.613 | cap1alo async0.8 econ | **UNDECIDED** best thin 0.613 | - |
| 394743d78562ab5f | C | global sync | d1 dl16 b2 | 1.00 | 0.502 | 0.477 | OVR L12->16 0.509 [0.483,0.533] | 0.953 | nan | decay3 cap4alo global | **R-CANDIDATE** refresh OVR 0.953 [0.891,1.000] M32 | PASS (conservative diff >= 0.37; teachers-removed 0.492, M32) |
| 17b093a7886431d8 | A | torus sync | d1 dl8 b4 | 1.00 | 0.499 | 0.484 | exact 0.508 [0.489,0.528] | 0.664 | nan | decay1 | **R-CANDIDATE** refresh OVR 0.630 [0.561,0.711] M64 | FAIL (paired diff lo99 0.018) |
| c5bceddafac4dc7b | C | global async | d5 dl16 b4 | 1.00 | 0.494 | 0.536 | OVR L8->16 0.508 [0.488,0.533] | 0.922 | nan | decay3 async0.8 global | **R-CANDIDATE** refresh OVR 0.922 [0.854,0.974] M32 | PASS (conservative diff >= 0.35; teachers-removed 0.490, M32) |
| ecf3945df0ad6537 | A | ring sync | d3 dl8 b4 | 1.00 | 0.501 | 0.516 | exact 0.508 [0.493,0.522] | 0.516 | 0.547 | decay3 cap4sat loss0.6 econ | **UNDECIDED** best thin 0.547 | - |
| d957d95c3a86fe53 | C | global async | d5 dl16 b4 | 1.00 | 0.502 | 0.531 | OVR L8->16 0.505 [0.483,0.526] | 0.961 | nan | decay3 async0.8 global | **R-CANDIDATE** refresh OVR 0.961 [0.906,1.000] M32 | PASS (conservative diff >= 0.39; teachers-removed 0.500, M32) |
| 2aefc9fef958812a | A | random async | d3 dl16 b2 | 1.00 | 0.496 | 0.484 | exact 0.505 [0.496,0.514] | 0.643 | nan | decay1 cap4alo async0.8 econ | **R-CANDIDATE** refresh OVR 0.633 [0.564,0.706] M64 | FAIL (paired diff lo99 0.039) |
| 79bc73b022e5d826 | A | global sync | d5 dl8 b4 | 1.00 | 0.506 | 0.516 | OVR L8->16 D1->2 0.503 [0.437,0.563] | 0.409 | 0.552 | decay3 cap4sat global econ | **UNDECIDED** best thin 0.552 | - |
| 7da1d985912ef131 | A | random async | d5 dl4 b2 | 1.00 | 0.496 | 0.531 | exact 0.502 [0.496,0.512] | 0.469 | 0.508 | decay3 cap4alo async0.8 econ | **UNDECIDED** best thin 0.508 | - |
| f6cfdf8240aa339a | A | ring async | d3 dl16 b4 | 1.00 | 0.511 | 0.516 | exact 0.501 [0.483,0.520] | 0.643 | nan | decay3 async0.5 econ | **R-CANDIDATE** refresh OVR 0.661 [0.599,0.723] M64 | PASS (paired diff lo99 0.104) |
| ba09f3510be6c9f7 | A | smallworld sync | d3 dl8 b4 | 1.00 | 0.491 | 0.448 | OVR L16->16 D1->2 0.501 [0.486,0.518] | 0.491 | 0.430 | decay1 | **UNDECIDED** best base 0.501 | - |
| 06e99bf21c0aca14 | A | ring sync | d2 dl4 b4 | 1.00 | 0.501 | 0.482 | OVR L12->16 D1->2 0.501 [0.486,0.513] | 0.474 | 0.448 | decay6 loss0.6 econ | **UNDECIDED** best base 0.501 | - |
| 56cdba0a6c46c1d3 | A | global async | d1 dl16 b4 | 1.00 | 0.506 | 0.464 | OVR L8->16 0.501 [0.492,0.510] | 0.482 | 0.479 | decay6 cap1sat loss0.3 async0.5 global econ | **UNDECIDED** best base 0.501 | - |
| 4b848d80ee0a7106 | A | smallworld async | d3 dl16 b4 | 1.00 | 0.500 | 0.508 | OVR L8->16 0.500 [0.500,0.500] | 0.477 | 0.521 | decay1 cap1sat async0.8 econ | **UNDECIDED** best thin 0.521 | - |
| 603723a7676b8e1d | A | smallworld async | d2 dl16 b4 | 1.00 | 0.500 | 0.536 | OVR L12->16 D1->2 0.500 [0.500,0.500] | 0.526 | 0.500 | decay3 async0.8 econ | **UNDECIDED** best refresh 0.526 | - |
| 964053bb4c9065fd | C | global sync | d2 dl8 b4 | 1.00 | 0.484 | 0.510 | exact 0.500 [0.500,0.500] | 0.503 | 0.505 | decay3 cap4sat global econ | **UNDECIDED** best thin 0.505 | - |
| 9b47d5378f2c9244 | C | global sync | d2 dl8 b4 | 1.00 | 0.499 | 0.464 | exact 0.500 [0.500,0.500] | 0.492 | 0.500 | decay3 cap4alo global econ | **UNDECIDED** best base 0.500 | - |
| b283e1cec4e52e7e | C | global async | d3 dl16 b2 | 1.00 | 0.500 | 0.564 | OVR L8->16 0.500 [0.500,0.500] | 0.523 | 0.523 | decay3 cap2alo loss0.3 async0.8 global econ | **UNDECIDED** best refresh 0.523 | - |
| cabf14291d28a3d7 | C | global sync | d2 dl8 b4 | 1.00 | 0.503 | 0.531 | exact 0.500 [0.500,0.500] | 0.490 | 0.510 | decay3 global econ | **UNDECIDED** best thin 0.510 | - |
| d09510b3e567a37d | A | global sync | d5 dl16 b4 | 1.00 | 0.503 | 0.490 | OVR L8->16 0.500 [0.500,0.500] | 0.505 | 0.505 | decay3 loss0.6 global | **UNDECIDED** best refresh 0.505 | - |
| d8bcfce07262128e | A | ring sync | d1 dl4 b4 | 1.00 | 0.499 | 0.510 | OVR L12->16 0.500 [0.500,0.500] | 0.503 | 0.539 | decay1 cap4sat | **UNDECIDED** best thin 0.539 | - |
| eb076f0d822f52c1 | C | torus sync | d3 dl16 b4 | 1.00 | 0.503 | 0.503 | exact 0.500 [0.500,0.500] | 0.680 | nan | decay1 cap1alo econ | **R-CANDIDATE** refresh OVR 0.663 [0.574,0.751] M64 | FAIL (paired diff lo99 0.017) |
| ebdbe504129fe914 | A | global async | d3 dl8 b4 | 1.00 | 0.495 | 0.505 | OVR L12->16 0.500 [0.500,0.500] | 0.500 | 0.500 | decay3 cap4alo loss0.6 async0.8 global econ | **UNDECIDED** best base 0.500 | - |
| f4e59e6154ea0c5a | A | random async | d3 dl16 b4 | 1.00 | 0.495 | 0.400 | OVR L8->16 0.500 [0.500,0.500] | 0.487 | 0.495 | decay3 cap1sat loss0.6 async0.8 econ | **UNDECIDED** best base 0.500 | - |
| f53a428a92d430b5 | A | global async | d1 dl4 b4 | 1.00 | 0.491 | 0.495 | OVR L8->16 0.500 [0.439,0.558] | 0.561 | 0.531 | decay6 loss0.3 async0.8 global econ | **UNDECIDED** best refresh 0.561 | - |
| 3f78ee89d5d6fb3c | A | global sync | d2 dl4 b4 | 1.00 | 0.501 | 0.473 | OVR L12->16 0.499 [0.490,0.508] | 0.493 | 0.482 | decay1 cap1alo loss0.3 global | **UNDECIDED** best base 0.499 | - |
| bda1a1bf2f3a927a | C | global async | d5 dl16 b4 | 1.00 | 0.480 | 0.464 | OVR L8->16 0.499 [0.475,0.521] | 0.948 | nan | decay3 cap1sat async0.8 global | **R-CANDIDATE** refresh OVR 0.948 [0.885,0.990] M32 | PASS (conservative diff >= 0.37; teachers-removed 0.490, M32) |
| 05fea1b55336dedf | A | smallworld sync | d5 dl16 b2 | 1.00 | 0.488 | 0.508 | exact 0.498 [0.474,0.523] | 1.000 | nan | decay3 econ | **R-CANDIDATE** refresh OVR 1.000 [1.000,1.000] M32 | PASS (conservative diff >= 0.50; teachers-removed 0.500, M32) |
| 75e32ae0d386af47 | A | random async | d3 dl16 b4 | 1.00 | 0.510 | 0.509 | exact 0.498 [0.479,0.518] | 0.523 | 0.464 | decay1 loss0.3 async0.8 econ | **UNDECIDED** best refresh 0.523 | - |
| 1dea05b393fc2da9 | A | random async | d2 dl16 b4 | 1.00 | 0.513 | 0.486 | exact 0.496 [0.488,0.503] | 0.469 | 0.534 | decay1 cap4alo async0.5 | **UNDECIDED** best thin 0.534 | - |
| 891dbf32ca704fed | A | ring sync | d3 dl8 b2 | 1.00 | 0.493 | 0.539 | OVR L16->16 D1->2 0.496 [0.478,0.513] | 0.598 | 0.547 | decay1 cap2sat loss0.3 econ | **UNDECIDED** best refresh 0.598 | - |
| cc9858540c527326 | A | global sync | d5 dl4 b4 | 1.00 | 0.522 | 0.471 | exact 0.494 [0.479,0.508] | 0.503 | 0.495 | decay3 cap2alo loss0.3 global econ | **UNDECIDED** best refresh 0.503 | - |
| fc6972d4930ea3f4 | A | torus async | d3 dl16 b2 | 1.00 | 0.508 | 0.445 | OVR L12->16 0.494 [0.474,0.515] | 0.523 | 0.484 | decay6 cap2sat async0.5 econ | **UNDECIDED** best refresh 0.523 | - |
| d99833cbd7fad41d | A | ring async | d1 dl16 b4 | 1.00 | 0.500 | 0.542 | OVR L12->16 0.492 [0.460,0.516] | 0.464 | 0.500 | decay6 cap1alo async0.5 econ | **UNDECIDED** best thin 0.500 | - |
| d3f360068a9aec81 | A | ring sync | d3 dl16 b4 | 1.00 | 0.493 | 0.539 | OVR L12->16 0.491 [0.480,0.503] | 0.495 | 0.490 | decay6 cap2sat loss0.3 econ | **UNDECIDED** best refresh 0.495 | - |
| f867ff454ef28ca9 | A | global async | d5 dl8 b4 | 1.00 | 0.475 | 0.492 | exact 0.490 [0.411,0.562] | 0.471 | 0.505 | decay6 async0.5 global econ | **UNDECIDED** best thin 0.505 | - |
| 124923338e434d70 | A | ring sync | d1 dl4 b4 | 0.67 | 0.506 | 0.495 | OVR L12->16 0.488 [0.417,0.559] | 0.487 | 0.521 | decay6 loss0.3 econ | **UNDECIDED** best thin 0.521 | - |
| 299a681d2e3cbee1 | A | random async | d2 dl16 b2 | 1.00 | 0.492 | 0.508 | exact 0.488 [0.404,0.572] | 0.934 | nan | decay6 async0.8 econ | **R-CANDIDATE** refresh OVR 0.934 [0.855,0.988] M32 | PASS (conservative diff >= 0.31; teachers-removed 0.508, M32) |
| cdc9405d347c3f22 | A | global sync | d3 dl4 b4 | 1.00 | 0.504 | 0.523 | exact 0.484 [0.422,0.549] | 0.490 | 0.458 | decay6 cap2sat loss0.3 global econ | **UNDECIDED** best refresh 0.490 | - |
| c9998fe48f9341a8 | A | global sync | d1 dl8 b4 | 1.00 | 0.488 | 0.503 | OVR L8->16 0.469 [0.404,0.542] | 0.523 | 0.495 | decay6 global | **UNDECIDED** best refresh 0.523 | - |
| 7b6b7f6958c4405d | A | ring sync | d2 dl8 b2 | 1.00 | 0.521 | 0.508 | exact 0.468 [0.377,0.555] | 0.580 | 0.695 | decay6 cap2sat loss0.3 | **UNDECIDED** best thin@64 0.622 | - |
| 6e8fb3bb64c1f689 | A | global async | d1 dl16 b2 | 1.00 | 0.517 | 0.637 | exact 0.467 [0.408,0.531] | 0.457 | 0.477 | cap2alo loss0.6 async0.5 global | **UNDECIDED** best thin 0.477 | - |
| 0ad0988d7b7e0076 | A | global async | d5 dl16 b4 | 1.00 | 0.504 | 0.510 | OVR L8->16 D1->2 0.458 [0.387,0.529] | 0.878 | nan | decay6 async0.8 global econ | **R-CANDIDATE** refresh OVR 0.878 [0.784,0.958] M32 | PASS (conservative diff >= 0.26; teachers-removed 0.474, M32) |
| 221042948e32063c | A | ring sync | d3 dl16 b2 | 1.00 | 0.510 | 0.484 | OVR L8->16 0.453 [0.391,0.520] | 0.656 | 0.555 | decay6 | **UNDECIDED** best refresh 0.656 | - |

{'PLANT-SOLVED': 3, 'UNDECIDED': 41, 'R-CANDIDATE': 14}
UNDECIDED tag counts {'loss0.3': 15, 'async0.5': 9, 'global': 20, 'econ': 30, 'decay6': 16, 'async0.8': 10, 'cap1sat': 4, 'loss0.6': 7, 'cap1alo': 3, 'decay3': 12, 'cap4sat': 4, 'cap4alo': 4, 'decay1': 7, 'cap2alo': 3, 'cap2sat': 5}
n undecided 41
