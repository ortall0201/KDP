# Auto-Load Latest Manuscript & Polished Folder Fix

## User Requirements
1. **Automatically load the LAST (most recent) manuscript** from `books/manuscripts/` folder
2. **Save polished manuscripts** to `books/polished-manuscripts/` folder instead of `manuscripts/`

## Changes Implemented

### 1. Added Two New Nodes

#### Node 40: List Manuscripts
- **Type**: HTTP Request (GitHub API)
- **Purpose**: Fetches list of all files in `books/manuscripts/` directory
- **API**: `GET https://api.github.com/repos/ortall0201/KDP/contents/books/manuscripts`
- **Position**: (460, 200)

#### Node 41: Find Latest Manuscript
- **Type**: Code
- **Purpose**: Sorts manuscripts by timestamp and selects the most recent one
- **Logic**:
  - Filters for `.txt` files only
  - Extracts timestamp from filename (format: `2026-01-04T08-32-49_fiction.txt`)
  - Sorts by timestamp descending (newest first)
  - Returns latest file metadata
- **Position**: (680, 200)
- **Output**:
  ```json
  {
    "latest_manuscript": "2026-01-04T08-32-49_fiction.txt",
    "manuscript_path": "books/manuscripts/2026-01-04T08-32-49_fiction.txt",
    "manuscript_url": "https://...",
    "total_manuscripts": 6,
    "all_manuscripts": ["2026-01-04...", "2026-01-03..."]
  }
  ```

### 2. Updated Existing Nodes

#### Load Manuscript (Node 2)
**Before:**
```json
{
  "filePath": "=books/manuscripts/{{ $json.input_filename }}"
}
```

**After:**
```json
{
  "filePath": "={{ $('Find Latest Manuscript').first().json.manuscript_path }}"
}
```
- Now dynamically loads the path from "Find Latest Manuscript" node
- No longer requires hardcoded filename

#### Configuration (Node 3)
**Before:**
```javascript
const input_filename = '2026-01-04T08-32-49_fiction.txt';
// ...
return {
  json: {
    input_filename: input_filename,
    // ...
  }
};
```

**After:**
```javascript
// Removed input_filename - no longer needed
return {
  json: {
    book_id: book_id,
    target_word_count: target_word_count,
    known_issues: known_issues,
    iteration: 0
  }
};
```

#### Commit to GitHub (Node 24)
**Before:**
```json
{
  "filePath": "=books/manuscripts/{{ $json.book_id }}_FINAL.txt",
  "commitMessage": "=Autonomous ghostwriting complete: ..."
}
```

**After:**
```json
{
  "filePath": "=books/polished-manuscripts/{{ $json.book_id }}_FINAL.txt",
  "commitMessage": "=Polished manuscript complete: ..."
}
```
- Changed save location from `manuscripts/` to `polished-manuscripts/`
- Updated commit message to reflect "Polished" status

### 3. Updated Workflow Connections

**Before:**
```
Start → Load Manuscript → Configuration → PHASE 1: Master Planner
     → Structured Logger
     → PROMPT nodes
```

**After:**
```
Start → List Manuscripts → Find Latest Manuscript → Load Manuscript → PHASE 1: Master Planner
     → Configuration (utility only, no connections out)
     → Structured Logger
     → PROMPT nodes
```

## New Workflow Flow

```
                    ┌─ Configuration (utility)
                    │
Start ──────────────┼─ Structured Logger (utility)
                    │
                    ├─ PROMPT nodes (utilities)
                    │
                    └─ List Manuscripts
                           │
                           ↓
                    Find Latest Manuscript
                           │
                           ↓
                    Load Manuscript
                           │
                           ↓
                    PHASE 1: Master Planner
                           │
                           ↓
                       [AI Pipeline]
                           │
                           ↓
                    Commit to GitHub
                           ↓
              books/polished-manuscripts/{book_id}_FINAL.txt
```

## Folder Structure

### Input (Auto-detected)
```
books/manuscripts/
├── 2026-01-03T23-45-16_fiction_Romance_Fantasy__Romantasy_.txt
├── 2026-01-03T23-50-00_fiction_Romance_Fantasy__Romantasy_.txt
├── 2026-01-03T23-52-44_fiction_Romance_Fantasy__Romantasy_.txt
├── 2026-01-04T00-04-40_fiction_Romance_Fantasy__Romantasy_.txt
├── 2026-01-04T07-22-05_fiction.txt
└── 2026-01-04T08-32-49_fiction.txt  ← LATEST (auto-selected)
```

### Output (New folder)
```
books/polished-manuscripts/
└── 2026-01-05T14-30-22_FINAL.txt  ← Generated with unique book_id
```

## Benefits

✅ **No manual filename configuration** - Workflow automatically finds latest manuscript
✅ **Sorted by timestamp** - Always processes the most recent file
✅ **Clean separation** - Raw manuscripts stay in `manuscripts/`, polished versions in `polished-manuscripts/`
✅ **Unique output names** - Each run generates new timestamped file (no overwrites)
✅ **Visibility** - Console logs show which manuscript was selected

## Console Output Example

When workflow runs:
```
ℹ️  Found 6 manuscript(s). Using latest: 2026-01-04T08-32-49_fiction.txt
```

## Total Nodes

**Before**: 38 nodes
**After**: 40 nodes (+2 for auto-discovery)

## Testing Checklist

After importing the workflow:
- [ ] Start trigger connects to List Manuscripts
- [ ] List Manuscripts → Find Latest Manuscript → Load Manuscript chain is connected
- [ ] No loose nodes appear
- [ ] GitHub OAuth configured for all GitHub nodes
- [ ] Test execution shows "Found X manuscript(s). Using latest: ..."
- [ ] Output saves to `books/polished-manuscripts/` folder

## Future Enhancements

If you want to process a specific manuscript instead of the latest:
1. Add a Webhook trigger with `filename` parameter
2. Add an If node to check if `filename` is provided
3. If yes, use provided filename; if no, use auto-detection

---

**Status:** ✅ ALL FIXES APPLIED
**Date:** 2026-01-05
**Auto-Discovery:** Enabled
**Output Folder:** `books/polished-manuscripts/`
**Ready to Import:** YES
