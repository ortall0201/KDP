# KDP Workflows - Which Files to Use

## ✅ WORKING WORKFLOWS (Use These)

### 1. Fiction Best Seller Research
**File:** `1-kdp-fiction-bestseller-research.json`

**Status:** ✅ Working perfectly - extracts REAL data from Amazon

**What it does:**
- Scrapes Amazon fiction best seller lists
- Extracts titles, prices, ratings, reviews for top 20 books in each category
- Analyzes patterns (common words, average stats)
- Generates research report saved to GitHub

**How to use:**
1. Import into n8n
2. Configure GitHub credentials in final node
3. Execute workflow
4. Check `books/research/` folder in GitHub for report

---

### 2. Fiction Content Generation
**File:** `2-kdp-fiction-SIMPLE-WORKING.json`

**Status:** ✅ Fixed and working - processes all 10 chapters correctly

**What it does:**
- Takes your book concept (based on best seller research)
- Generates detailed story outline using GPT-4o
- Creates 10 chapters (~1,800-2,000 words each)
- Compiles complete manuscript (~18,000-20,000 words)
- Saves to GitHub automatically

**How to use:**
1. Import into n8n
2. Edit "Set Book Concept" node:
   - Change `book_concept` to your story idea
   - Change `genre` if needed
   - Change `target_words` if needed (default: 18000)
3. Configure GitHub credentials in "Commit to GitHub" node
4. Execute workflow (takes 15-20 minutes)
5. Check `books/manuscripts/` folder in GitHub for completed manuscript

**Key Fix:** Uses smart compilation logic that waits for all 10 chapters before compiling. See `WORKFLOW-2-FIX-EXPLANATION.md` for technical details.

---

## ❌ BROKEN WORKFLOWS (Do NOT Use)

### `2-kdp-fiction-content-generation.json`
**Problem:** Only processes 1 chapter instead of 10
**Reason:** Compile node executes too early due to streaming execution
**Status:** DEPRECATED - Use `2-kdp-fiction-SIMPLE-WORKING.json` instead

### `2-kdp-fiction-content-generation-FIXED.json`
**Problem:** Still only processes 1 chapter
**Reason:** splitInBatches Output 1 not passing all items correctly
**Status:** DEPRECATED - Use `2-kdp-fiction-SIMPLE-WORKING.json` instead

---

## 🔜 COMING SOON

### 3. Cover Design
**File:** `3-kdp-cover-design-GPT-IMAGE-1.5.json`

**Status:** Not yet created

**What it will do:**
- Generate book cover using GPT-Image-1.5
- Based on best seller cover styles
- Professional-looking cover art
- Ready for Canva touch-up (add title text, author name)

---

## Quick Start Guide

### Complete KDP Fiction Publishing Workflow:

1. **Research Best Sellers:**
   - Run `1-kdp-fiction-bestseller-research.json`
   - Review report in `books/research/`
   - Pick hot category (look for avg 4.0-4.5 stars, 50-500 reviews)

2. **Generate Manuscript:**
   - Create book concept mimicking successful patterns
   - Edit "Set Book Concept" node in `2-kdp-fiction-SIMPLE-WORKING.json`
   - Run workflow (15-20 minutes)
   - Download manuscript from `books/manuscripts/`

3. **Polish with Human Editor:**
   - Post job on Upwork.com
   - Budget: $50-200
   - Provide manuscript + outline
   - Ask editor to improve dialogue, pacing, character depth

4. **Generate Cover:**
   - Use Workflow 3 (coming soon)
   - Or create manually in Canva

5. **Publish on KDP:**
   - Upload edited manuscript
   - Upload cover
   - Check AI disclosure box
   - Launch FREE to get reviews
   - Add price after 10-20 reviews

---

## Technical Notes

### n8n Streaming Execution Issue
The broken workflows had a fundamental issue with n8n's execution model:
- n8n processes items as they stream through nodes
- Compile node was executing after first item arrived
- Solution: Smart logic that returns empty array until all items ready

### Batching Configuration
The working workflow uses HTTP Request batching:
```json
"options": {
  "batching": {
    "batch": {
      "batchSize": 1,
      "batchInterval": 1000
    }
  }
}
```
This processes 1 chapter at a time with 1-second delays (prevents rate limiting).

### Chapter Tracking
Format Chapter node uses `$itemIndex` to preserve chapter numbers:
```javascript
const originalItems = $('Create Chapter Items').all();
const chapterNumber = originalItems[$itemIndex].json.chapter_number;
```

---

## Support Files

- `FICTION-BESTSELLER-STRATEGY.md` - Complete strategy overview
- `WORKFLOW-2-FICTION-GENERATION.md` - Detailed Workflow 2 instructions
- `WORKFLOW-2-FIX-EXPLANATION.md` - Technical explanation of the fix

---

**For questions or issues, check the documentation files in the main KDP directory.**
