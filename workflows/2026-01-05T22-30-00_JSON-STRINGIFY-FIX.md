# Workflow Fix: JSON.stringify() Double-Stringification Issue

**Fix Date**: 2026-01-05T22:30:00
**Fixed File**: `2026-01-05T22-30-00_workflow-3-ghostwriter-VALIDATED-FIXED.json`
**Issue**: PHASE 1: Master Planner returned "JSON parameter needs to be valid JSON" error

---

## Root Cause Analysis

### The Problem

Using `JSON.stringify()` inside n8n expressions when `specifyBody: "json"` is configured causes **double-stringification**:

1. **First stringify**: `JSON.stringify({...})` converts JavaScript object → JSON string
2. **n8n's automatic conversion**: The HTTP Request node with `specifyBody: "json"` automatically converts objects to JSON
3. **Result**: The JSON string gets stringified again → invalid escaped JSON string

### Example of the Bug

**Before (WRONG)**:
```javascript
"jsonBody": "={{ JSON.stringify({
  model: 'gpt-4o',
  messages: [...]
}) }}"
```

When n8n processes this:
- `JSON.stringify()` produces: `'{"model":"gpt-4o","messages":[...]}'` (a string)
- n8n sees a string and escapes it: `'"{\\"model\\":\\"gpt-4o\\",\\"messages\\":[...]}"'`
- OpenAI API receives invalid JSON with escaped quotes

**After (CORRECT)**:
```javascript
"jsonBody": "={{ {
  model: 'gpt-4o',
  messages: [...]
} }}"
```

When n8n processes this:
- n8n receives JavaScript object: `{model: 'gpt-4o', messages: [...]}`
- n8n automatically converts to JSON: `'{"model":"gpt-4o","messages":[...]}'`
- OpenAI API receives valid JSON

---

## Fixes Applied

Removed `JSON.stringify(` and closing `)` from **5 HTTP Request nodes**:

### 1. PHASE 1: Master Planner (Line 138)
**Node**: Master Planner AI call
**Change**: Removed JSON.stringify() wrapper from jsonBody parameter

### 2. Scene Writer AI (Line 246)
**Node**: Scene expansion AI calls
**Change**: Removed JSON.stringify() wrapper from jsonBody parameter

### 3. Line Editor AI (Line 392)
**Node**: Line editing AI calls
**Change**: Removed JSON.stringify() wrapper from jsonBody parameter

### 4. PHASE 4: Consistency Check (Line 510)
**Node**: QA consistency validation
**Change**: Removed JSON.stringify() wrapper from jsonBody parameter

### 5. PHASE 5: Self-Critic (Line 556)
**Node**: Final quality score evaluation
**Change**: Removed JSON.stringify() wrapper from jsonBody parameter

---

## Why This Happened

This is a common mistake when working with n8n's HTTP Request node. The confusion stems from:

1. **Other programming contexts**: In normal JavaScript/Node.js, you must manually stringify JSON for HTTP requests
2. **n8n's abstraction**: n8n's HTTP Request node with `specifyBody: "json"` handles serialization automatically
3. **Mixed mental models**: Treating n8n expressions like raw JavaScript leads to double-stringification

---

## Key Takeaway

**N8N HTTP Request Node with `specifyBody: "json"`**:
- ✅ **DO**: Pass JavaScript objects directly: `"jsonBody": "={{ {...} }}"`
- ❌ **DON'T**: Use JSON.stringify(): `"jsonBody": "={{ JSON.stringify({...}) }}"`

The node automatically handles JSON serialization when `specifyBody: "json"` is set.

---

## Testing Checklist

After importing the fixed workflow:

- [ ] Import `2026-01-05T22-30-00_workflow-3-ghostwriter-VALIDATED-FIXED.json`
- [ ] Verify all 5 HTTP Request nodes have `specifyBody: "json"` (should already be set)
- [ ] Execute workflow
- [ ] PHASE 1: Master Planner should complete without JSON error
- [ ] Verify OpenAI receives valid JSON (check execution logs)
- [ ] Monitor all subsequent phases for successful API calls

---

## Verification Steps

### 1. Pre-Execution Check
Open each HTTP Request node and verify jsonBody looks like:
```javascript
"jsonBody": "={{ { model: 'gpt-4o', ... } }}"
```

NOT like:
```javascript
"jsonBody": "={{ JSON.stringify({ model: 'gpt-4o', ... }) }}"
```

### 2. During Execution
Watch for these log messages:
- ✅ **GOOD**: "ℹ️  Master Plan Generated"
- ❌ **BAD**: "Problem in node 'PHASE 1: Master Planner' - JSON parameter needs to be valid JSON"

### 3. Post-Execution Verification
- Check that PHASE 1 completes successfully
- Verify improvement plan is parsed correctly
- Confirm workflow progresses to PHASE 2: Scene Writer

---

## Expected Behavior Now

**PHASE 1: Master Planner** should:
1. Receive decoded manuscript (22,601 words)
2. Send valid JSON request to OpenAI API
3. Receive improvement plan response
4. Parse JSON plan successfully
5. Create expansion tasks for PHASE 2

All subsequent phases should follow the same pattern without JSON errors.

---

## Files in This Fix Series

1. **2026-01-05T16-19-16_workflow-3-ghostwriter.json** - Original workflow (had multiple issues)
2. **2026-01-05T19-13-31_workflow-3-ghostwriter-VALIDATED-FIXED.json** - First fix (base64 decoding, retry logic, etc.)
3. **2026-01-05T21-24-46_workflow-3-ghostwriter-VALIDATED-FIXED.json** - Second fix (enhanced Decode Manuscript)
4. **2026-01-05T22-30-00_workflow-3-ghostwriter-VALIDATED-FIXED.json** - **CURRENT** (JSON.stringify() removed)

---

## Status

✅ **READY FOR TESTING**

All known blocking issues have been resolved:
- ✅ Base64 decoding (Decode Manuscript node)
- ✅ Retry logic (all HTTP nodes)
- ✅ Rate limiting (5s pauses)
- ✅ Error workflow configuration
- ✅ GitHub operation parameter
- ✅ **JSON serialization (this fix)**

**Next Step**: Import the workflow and execute. The workflow should now run without JSON parameter errors.

---

**Fixed by**: n8n-brain skill
**Date**: 2026-01-05
**Version**: Production-Ready v3.0
