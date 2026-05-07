class BaseRenderer:
    def render(self, state, fmt="text", context=None):
        if fmt == "json":
            import json
            return json.dumps(state.to_dict() if hasattr(state, 'to_dict') else state, indent=2, default=str)
        elif fmt == "markdown":
            return self._markdown(state)
        return self._text(state)

    def _text(self, state):
        lines = [f"SAGE Domain: {getattr(state, 'domain', 'unknown')}"]
        ops = getattr(state, 'operations', [])
        lines.append(f"Operations: {len(ops)}")
        for op in ops[:20]:
            name = getattr(op, 'op', str(op))
            lines.append(f"  - {name}")
        return "\n".join(lines)

    def _markdown(self, state):
        lines = [f"# SAGE {getattr(state, 'domain', 'Report')}", ""]
        ops = getattr(state, 'operations', [])
        lines.append(f"**Operations**: {len(ops)}", "")
        for op in ops[:20]:
            name = getattr(op, 'op', str(op))
            lines.append(f"- `{name}`")
        return "\n".join(lines)
