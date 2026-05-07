_registry = {}

def register_domain(domain):
    _registry[domain.name] = domain

def get_domain(name):
    return _registry.get(name)

def list_domains():
    return list(_registry.keys())

def clear_registry():
    _registry.clear()
