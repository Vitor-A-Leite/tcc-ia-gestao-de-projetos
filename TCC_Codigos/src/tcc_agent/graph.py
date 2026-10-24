import json
from collections import defaultdict, deque
from pathlib import Path


class ProjectGraph:
    """Carrega o grafo do projeto e permite percorrer dependências."""

    def __init__(self, nodes: list[dict], edges: list[dict]):
        self.nodes = {node["id"]: node for node in nodes}
        self.edges = edges
        self.adjacency = defaultdict(list)

        for edge in edges:
            self.adjacency[edge["source"]].append(
                {"target": edge["target"], "type": edge["type"]}
            )

    @classmethod
    def from_json(cls, path: str | Path) -> "ProjectGraph":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(data["nodes"], data["edges"])

    def has_entity(self, entity_id: str) -> bool:
        return entity_id in self.nodes

    def entity_name(self, entity_id: str) -> str:
        return self.nodes.get(entity_id, {}).get("name", entity_id)

    def downstream(self, start_ids: list[str], max_depth: int = 4, on_step=None) -> tuple[list[str], dict[str, list[str]]]:
        """Retorna entidades a jusante e o caminho usado para alcançá-las.

        O método usa busca em largura (BFS). A profundidade máxima evita que
        todo o projeto seja marcado como impactado por um único evento.
        """
        visited = set(start_ids)
        queue = deque((sid, 0, [sid]) for sid in start_ids if sid in self.nodes)
        impacted = []
        trace: dict[str, list[str]] = {}

        while queue:
            current, depth, path = queue.popleft()
            if depth >= max_depth:
                continue

            for edge in self.adjacency.get(current, []):
                target = edge["target"]
                if target in visited:
                    continue
                visited.add(target)
                new_path = path + [target]
                impacted.append(target)
                trace[target] = new_path
                if on_step is not None:
                    on_step({"source": current, "target": target, "relation": edge["type"],
                             "path": new_path, "depth": depth + 1})
                queue.append((target, depth + 1, new_path))

        return impacted, trace
