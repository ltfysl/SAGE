class BaseState:
    def __init__(self, domain=None, operations=None, metadata=None):
        self.domain = domain
        self.operations = operations or []
        self.metadata = metadata or {}
        self._op_index = {}
        self._tag_index = {}
        self._rebuild_indexes()

    def add_operation(self, op):
        self.operations.append(op)
        self._index_op(op)

    def _index_op(self, op):
        ot = getattr(op, 'op', None) or op.get('op', '') if isinstance(op, dict) else ''
        if ot:
            self._op_index.setdefault(ot, []).append(op)
        tags = getattr(op, 'tags', None) or op.get('tags', []) if isinstance(op, dict) else []
        for tag in tags:
            self._tag_index.setdefault(tag, []).append(op)

    def _rebuild_indexes(self):
        self._op_index.clear()
        self._tag_index.clear()
        for op in self.operations:
            self._index_op(op)

    def find_by_op(self, op_type):
        return self._op_index.get(op_type, [])

    def find_by_tag(self, tag):
        return self._tag_index.get(tag, [])

    def to_dict(self):
        return {
            'domain': self.domain,
            'ops_count': len(self.operations),
            'operations': [o.to_dict() if hasattr(o, 'to_dict') else o for o in self.operations],
            'metadata': self.metadata,
        }
