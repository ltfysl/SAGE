import sys;sys.path.insert(0,"src");from sage.domains.codemap.changed_analysis import analyze_changes
def test_analyze_works(): r=analyze_changes("."); assert "changed_files" in r; assert "diff_stat" in r
def test_analyze_error_on_nongit(): r=analyze_changes("/tmp"); assert "error" in r
