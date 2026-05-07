import sys;sys.path.insert(0,"src");from sage.domains.codemap.project_index import load_index, save_index, list_projects, get_project_info
def test_load_empty(): assert isinstance(load_index(), dict)
def test_save_load(): d={"test":"value"}; save_index(d); assert load_index().get("test")=="value"; save_index({})
def test_list_projects(): assert isinstance(list_projects(), list)
