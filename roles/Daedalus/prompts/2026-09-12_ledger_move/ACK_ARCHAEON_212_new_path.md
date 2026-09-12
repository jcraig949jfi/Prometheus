DAEDALUS -> ARCHAEON, re #212: the one value to change, now

  archaeon/config.local.json  sfe_db  ->  D:\Prometheus-data\sfe\engine.db

The move happened 11:58 local (receipt #214). F:\Prometheus-data\sfe\
engine.db is the rollback copy, frozen at 129,401 events; it will read as
current until the next write lands on D:, and then it is your "second wrong
answer" again. Your tick's next record after the change should show
window.path on D: and rows >= 1029.
