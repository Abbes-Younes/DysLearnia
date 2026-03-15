from typing import List, Dict, Any

# maps each agent to what it needs from state
AGENT_INPUTS = {
    "simplify":   ["raw_text", "reading_level"],
    "quiz":       ["simplified_text", "raw_text", "reading_level"],
    "hint":       ["simplified_text", "raw_text", "reading_level", "user_question"],
    "gamify":     ["quiz", "reading_level", "progress"],
}

# maps each agent to what it writes to state
AGENT_OUTPUTS = {
    "simplify":   ["simplified_text"],
    "quiz":       ["quiz"],
    "hint":       ["hint"],
    "gamify":     ["gamification"],
}

VALID_AGENTS = set(AGENT_INPUTS.keys())


def topological_sort(nodes: List[str], edges: List[Dict]) -> List[str]:
    """
    Sort agents into execution order based on edges.
    Example:
      nodes: ["simplify", "quiz", "hint"]
      edges: [{"from":"simplify","to":"quiz"}, {"from":"simplify","to":"hint"}]
      result: ["simplify", "quiz", "hint"]
    """
    from collections import defaultdict, deque

    in_degree = {n: 0 for n in nodes}
    graph = defaultdict(list)

    for edge in edges:
        src = edge["from"]
        dst = edge["to"]
        if src in in_degree and dst in in_degree:
            graph[src].append(dst)
            in_degree[dst] += 1

    # start with nodes that have no dependencies
    queue = deque([n for n in nodes if in_degree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(nodes):
        raise ValueError("Pipeline has a cycle — check your connections.")

    return order


def validate_pipeline(nodes: List[str], edges: List[Dict]) -> List[str]:
    """
    Check all nodes are valid agent names.
    Returns list of errors (empty = valid).
    """
    errors = []
    for node in nodes:
        if node not in VALID_AGENTS:
            errors.append(f"Unknown agent: '{node}'. Valid: {list(VALID_AGENTS)}")
    return errors


def run_pipeline(nodes: List[str], edges: List[Dict], initial_state: Dict, graph) -> Dict:
    errors = validate_pipeline(nodes, edges)
    if errors:
        raise ValueError("\n".join(errors))

    order = topological_sort(nodes, edges)
    print(f"[pipeline] Execution order: {order}")

    state = dict(initial_state)
    state["agents_run"] = []

    for agent in order:
        print(f"[pipeline] Running: {agent}")

        # build a clean invoke payload — only what the graph needs
        invoke_payload = {
            "task": agent,
            "text": state.get("simplified_text") or state.get("raw_text", ""),
            "raw_text": state.get("raw_text", ""),
            "simplified_text": state.get("simplified_text") or "",
            "reading_level": state.get("reading_level", "adult"),
            "user_question": state.get("user_question") or "",
            "progress": state.get("progress"),
            "quiz": state.get("quiz"),
        }

        print(f"[pipeline] task={agent} text_len={len(invoke_payload['text'])}")
        result = graph.invoke(invoke_payload)

        # merge results back into shared state
        state.update(result)
        state["agents_run"].append(agent)
        print(f"[pipeline] {agent} complete — output keys: {[k for k,v in result.items() if v]}")

    return state