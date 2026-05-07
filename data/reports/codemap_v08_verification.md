# CodeMap v0.8 Verification Report

## 1. Latest Commit
- **Hash**: `adeb463`
- **Message**: "Add CodeMap Cursor IDE integration"
- **Files changed**: `src/sage/cli.py` (+35), `src/sage/domains/codemap/cursor_integration.py` (+111)
- **Is CodeMap v0.8**: Yes — this is the Cursor integration commit.

## 2. Parser Improvements (UNSTAGED)
The safety-web-3 pattern improvements are in `src/sage/domains/codemap/php_parser.py` but were **never committed**. Changes:
- `app(ClassName::class)` detection → CONTROLLER_USES_SERVICE
- `Model::firstOrNew()` → READS_TABLE + WRITES_TABLE
- `$var->store()` on model instances → WRITES_TABLE

These changes exist as unstaged modifications and were used during the `--force-scan` regeneration.

## 3. Context Quality (Current `.cursor/sage-context.md`)

**Codmap path**: `data/codemaps/safety-web-3_codemap.json` (NOT v04 — correct)

**Top files:**
1. Scorm12Controller.php (108) ✓
2. Scorm12Manifest.php (76) ✓
3. Scorm12NavigationItem.php (70) ✓
4. ScormTest.php (68) ✓
5. scorm12.js (63) ~ (frontend, but relevant)
6-9: UserGroup/Assignment/DeactivateCourse tests (NOISE)
10: course_progresses migration ✓

**Flow**: route → controller only. **Does NOT extend beyond.**
Root cause: FlowBuilder step 3 filters edges for "Service" keyword. `Scorm12Manifest` is a utility class, not a "Service" → edge is ignored.

**Relevant files**: Controller, manifest, navigation item, test, migration are present. But CourseProgress/LearningContentProgress models are missing from top 20.

## 4. Verdict
**Context quality: MARGINAL.** 
- Controller ranked #1 ✓
- Flow stops at route→controller (FlowBuilder bug)
- CourseProgress/LearningContentProgress models not ranked
- Unrelated test noise at positions 6-9
- Parser improvements are unstaged/uncommitted

## 5. Remaining CodeMap Bug
FlowBuilder step 3: `"Service" in dst` filter is too strict. `CONTROLLER_USES_SERVICE` edges to non-"Service" classes (like `Scorm12Manifest`) are ignored. Fix: allow any `CONTROLLER_USES_SERVICE` edge to be followed, not just those with "Service" in the target name.

## 6. Recommended Next Action
1. Commit the unstaged php_parser.py improvements
2. Fix FlowBuilder to follow all CONTROLLER_USES_SERVICE edges
3. Re-scan safety-web-3 and regenerate context
4. Verify flow extends to Scorm12Manifest → CourseProgress
