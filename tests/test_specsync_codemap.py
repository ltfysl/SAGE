import sys;sys.path.insert(0,"src");from sage.domains.specsync.codemap_linker import load_codemap,build_coverage_report;from sage.domains.specsync.domain import SpecSyncDomain
d=SpecSyncDomain()
def test_build_report():
 ops=d.compile("data/samples/specsync/invoicing_app")
 cm=load_codemap("data/codemaps/laravel_codemap_v07.json")
 r=build_coverage_report(ops,cm)
 assert r["tasks_total"]>=5
 assert r["tasks_done"]>=1
 assert "missing_test_coverage" in r
 assert "recommendations" in r
