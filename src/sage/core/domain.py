class SageDomain:
    def __init__(self, name, version="0.1.0", description=""):
        self.name = name
        self.version = version
        self.description = description

    def compile(self, input_data, context=None):
        raise NotImplementedError

    def verify(self, operations, context=None):
        from sage.core.verifier import DefaultVerifier
        return DefaultVerifier().verify(operations, context)

    def build_state(self, operations, context=None):
        from sage.core.state import BaseState
        state = BaseState(domain=self.name)
        for op in operations:
            state.add_operation(op)
        return state

    def answer(self, state, question, context=None):
        raise NotImplementedError

    def render(self, state, fmt="text", context=None):
        from sage.core.renderer import BaseRenderer
        return BaseRenderer().render(state, fmt)

    def __repr__(self):
        return f"SageDomain({self.name!r} v{self.version})"
