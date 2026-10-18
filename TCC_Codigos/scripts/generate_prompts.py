import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from tcc_agent.baseline import build_baseline_prompt, build_entity_dictionary


def main() -> None:
    scenarios = json.loads((ROOT / "data/scenarios_ground_truth.json").read_text(encoding="utf-8"))
    entity_dict = build_entity_dictionary(ROOT / "data/project_graph.json")
    out_dir = ROOT / "outputs/prompts"
    out_dir.mkdir(parents=True, exist_ok=True)

    for scenario in scenarios:
        prompt = build_baseline_prompt(scenario["source_text"], entity_dict)
        (out_dir / f"{scenario['scenario_id']}.txt").write_text(prompt, encoding="utf-8")

    print(f"{len(scenarios)} prompts gerados em {out_dir}")


if __name__ == "__main__":
    main()
