"""Quick Apollo status snapshot for the bake-off."""
import sys
sys.path.insert(0, "D:\\Prometheus\\scripts")
import agora_persist
r = agora_persist.read_agent("Apollo")
if not r:
    print("NO HEARTBEAT")
    sys.exit(0)
sj = r["status_json"]
print(f"gen={sj['generation']} phase={sj['phase']} gen_time={sj['gen_time_s']}s "
      f"map_elites={sj['map_elites_size']} ncd_w={sj['ncd_weight']} "
      f"best_fitness={sj['best_fitness_vector']} median={sj['median_fitness']}")
print(f"last_heartbeat={r['last_heartbeat']} pid={r['pid']}")
