# H1 beta sizing: the 3- and 4-input Boolean universes, enumerated

table_id sha256:750fe32eca1b52b2b8e38a2fd131e21ed8eeaedafe5aecf2734d11d487e70bc2. Emitted by proteus/eval/emit_universe_table.py; every number is exact (no sampling). Size = node count, the kind's own measure.

## n = 3: 8 cases, 256 tables

    size  first_reached  cumulative  fraction   expressions_thru_size
       1              5           5    0.0195                       5
       2              3           8    0.0312                      10
       3              9          17    0.0664                      90
       4             21          38    0.1484                     320
       5             21          59    0.2305                    3025
       6             81         140    0.5469                   15030
       7             43         183    0.7148                  134285
       8             43         226    0.8828                       -
       9             18         244    0.9531                       -
      10             12         256    1.0000                       -
    saturates at size 10

    witness pool (reachable inputs = complement of the seeded prefix)
    K   constant seed   per-task 24 tasks   per-task 64 tasks   tasks to full
    4             4/8                 8/8                 8/8               4
    8             0/8                 0/8                 0/8            None

    verification cost (measured with the evaluator; formula n + nodes + 3 per case)
    nodes  ops/case measured  ops/case predicted  ops total  cases  parity
        1                [7]                   7         56      8  PASS
        2                [8]                   8         64      8  PASS
        3                [9]                   9         72      8  PASS
        4               [10]                  10         80      8  PASS
        5               [11]                  11         88      8  PASS
        6               [12]                  12         96      8  PASS
        7               [13]                  13        104      8  PASS

## n = 4: 16 cases, 65536 tables

    size  first_reached  cumulative  fraction   expressions_thru_size
       1              6           6    0.0001                       6
       2              4          10    0.0002                      12
       3             18          28    0.0004                     126
       4             42          70    0.0011                     456
       5             84         154    0.0023                    4998
       6            324         478    0.0073                   25524
       7            415         893    0.0136                  260430
       8           1483        2376    0.0363                       -
       9           2124        4500    0.0687                       -
      10           5764       10264    0.1566                       -
      11           7217       17481    0.2667                       -
      12          13267       30748    0.4692                       -
      13          12175       42923    0.6550                       -
      14          15195       58118    0.8868                       -
      15           5464       63582    0.9702                       -
      16           1910       65492    0.9993                       -
      17             44       65536    1.0000                       -
    saturates at size 17

    witness pool (reachable inputs = complement of the seeded prefix)
    K   constant seed   per-task 24 tasks   per-task 64 tasks   tasks to full
    4           12/16               16/16               16/16               4
    8            8/16               16/16               16/16               5

    verification cost (measured with the evaluator; formula n + nodes + 3 per case)
    nodes  ops/case measured  ops/case predicted  ops total  cases  parity
        1                [8]                   8        128     16  PASS
        2                [9]                   9        144     16  PASS
        3               [10]                  10        160     16  PASS
        4               [11]                  11        176     16  PASS
        5               [12]                  12        192     16  PASS
        6               [13]                  13        208     16  PASS
        7               [14]                  14        224     16  PASS

