# SAGE CodeMap — safety-web-3 Analysis Review

## 1. Scan Summary

| Metric | Value |
|--------|-------|
| Files scanned | 974 |
| Operations | 10,780 |
| Languages | PHP, JavaScript, Vue, JSON, YAML, Markdown, Env |
| Frameworks | Laravel, Vue |
| Graph nodes | 4,873 |
| Graph edges | 4,562 |
| Top edge types | IMPORTS (3,718), WRITES_TABLE (338), DEFINES (260), CALLS (230) |

## 2. Ignore Verification

| Directory | Files | Status |
|-----------|-------|--------|
| vendor/ | 0 | ✓ Ignored |
| node_modules/ | 0 | ✓ Ignored |
| .git/ | 0 | ✓ Ignored |
| storage/ | 0 | ✓ Ignored |
| bootstrap/cache/ | 0 | ✓ Ignored |

## 3. Key Findings

### What Worked
- **Tenant database search**: Correctly ranked `Models/Tenant/`, `ClientTenantSwitch/`, `SeedTenantDatabase.php` highly
- **WRITES_TABLE for course_progresses**: Found 10 migration operations that alter the table structure
- **260 routes detected**: Covers both route definitions and middleware/prefix groups
- **Framework detection**: Correctly identified Laravel + Vue
- **Graph edges**: 4,562 edges showing real architectural relationships

### What Failed
- **"SCORM"/"assignments"/"certificates" feature search**: Returns ALL 974 files instead of filtering. The scoring differs but every file appears. Root cause: `_search_fulltext` iterates all files and assigns non-zero scores too liberally.
- **public/js/app.js dominates scores**: This compiled JS bundle (1,482 lines of minified code) matches every keyword and skews all feature searches. Should be excluded from scoring or deprioritized.
- **No runtime WRITES_TABLE**: Only migration-level table writes detected. Service-level writes (`CourseProgress::updateOrCreate()`) are not captured because the parser only detected them as `CALLS_METHOD`.

## 4. Architecture Insights

- The project uses a **multi-tenant architecture** with `app/Classes/ClientTenantSwitch/` for tenant data routing
- `app/Models/Tenant/` contains per-tenant models (User, Client, Assignment, CourseProgress)
- `app/Models/Main/` contains shared models
- `app/Http/Controllers/TenantAPI/` exposes tenant-scoped REST endpoints
- SCORM-related files include `ExtractScormPackage.php`, SCORM controllers, and course progress services

## 5. Top 5 CodeMap v0.4 Improvements Needed

1. **Exclude compiled/bundled files from scoring**: `public/js/app.js`, `public/css/app.css`, and any file > 500KB should be skipped or heavily deprioritized
2. **Filter search results to top-N by relevance**: Show only the top 20 files by score, not all 974. Add a minimum relevance threshold.
3. **Route classification**: Separate actual endpoint routes from middleware/prefix/group definitions. Show HTTP method + path for real routes.
4. **Runtime table writes**: Detect `Model::updateOrCreate()`, `DB::table()->insert()`, `$model->save()` as WRITES_TABLE with table name resolution from model classes
5. **Tenant-awareness**: Add multi-tenant pattern detection. Flag files in `app/Models/Tenant/` and `app/Classes/ClientTenantSwitch/` as tenant-scoped.

## 6. Generated Files

- `data/codemaps/safety_web_3_codemap.json` — 974-file codemap (gitignored)
- `data/reports/safety_web_3_codemap_review.md` — this report (gitignored)
