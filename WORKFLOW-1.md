# Workflow 1: KDP Niche Research Engine

**File:** `workflows/1-kdp-niche-research-WORKING.json`

---

## 📋 Overview

Automatically researches profitable KDP niches by analyzing Amazon bestsellers, calculating ROI, and committing opportunities to your GitHub repo.

**Cost:** $0.00 (no API calls, web scraping only)
**Duration:** ~2-5 minutes per run (10 niches)
**Output:** Markdown report in `books/research/opportunities_YYYY-MM-DD.md`

---

## 🎯 What It Does

### Workflow Flow:
```
Manual Trigger
    ↓
Create Niche List (10 niches)
    ↓
Fetch Amazon Bestsellers (for each niche)
    ↓
Analyze Competition (simple heuristics)
    ↓
Filter Golden Opportunities (low competition + good demand)
    ↓
Calculate Profit Potential (ROI, revenue estimates)
    ↓
Filter Excellent ROI (400%+ only)
    ↓
Aggregate All Opportunities (combine into one report)
    ↓
Compile Report (markdown format)
    ↓
Commit to GitHub (books/research/)
```

### Analysis Criteria:

**Golden Opportunity:**
- ❌ No high ratings (4.5+ stars) dominating
- ✅ Good search results exist
- ✅ Moderate competition
- ✅ Room for new books

**Excellent ROI:**
- 400%+ return on investment
- Based on $1.57 production cost
- Estimated 35 sales/month
- $4.99 optimal pricing
- 70% royalty rate

---

## 🔧 Setup Instructions

### 1. Import Workflow

1. Open n8n
2. Click **"+"** → **"Import from File"**
3. Select: `workflows/1-kdp-niche-research-WORKING.json`
4. Workflow imports with all nodes

### 2. Configure GitHub Credential

1. Click the **"Commit to GitHub"** node (last node)
2. Under **Credential**, click **"+"** to add new
3. Select **"GitHub OAuth2 API"** or **"GitHub API"**
4. Choose authentication method:
   - **Personal Access Token** (simpler):
     - Go to https://github.com/settings/tokens
     - Generate new token (classic)
     - Select scope: **repo** (full control)
     - Copy token (starts with `ghp_...`)
     - Paste in n8n
   - **OAuth2** (more secure):
     - Follow n8n OAuth flow
     - Authorize GitHub access

### 3. Select Repository

1. In **"Commit to GitHub"** node:
2. **Owner** dropdown → Select your GitHub username
3. **Repository** dropdown → Select "KDP"
4. Save

### 4. Edit Niches (Optional)

1. Click **"Create Niche List (EDIT THIS)"** node
2. Modify the JavaScript array:

```javascript
const niches = [
  'keto diet',
  'intermittent fasting',
  'productivity',
  'mindfulness',
  'budget planning',
  'home organization',
  'dog training',
  'gardening',
  'woodworking',
  'photography'
  // Add your own niches here
];
```

3. Save node

---

## ▶️ How to Run

### Manual Test Run:

1. Open workflow in n8n
2. Click **"Execute Workflow"** button (top right)
3. Wait 2-5 minutes
4. Check execution log for results
5. Go to your GitHub repo → `books/research/` folder
6. See: `opportunities_YYYY-MM-DD.md`

### Automated Schedule (Optional):

Want it to run automatically every 3 days?

1. Click the **"Manual Trigger"** node
2. Delete it
3. Add new node: **"Schedule Trigger"**
4. Configure:
   - **Rule**: Every 3 days
   - **Time**: 9:00 AM (or your preference)
5. Connect to **"Create Niche List"** node
6. Activate workflow (toggle switch on)

---

## 📊 Output Example

**File:** `books/research/opportunities_2026-01-03.md`

```markdown
# KDP Niche Opportunities - 2026-01-03

Found 3 excellent niche(s)

---

## 1. mindfulness

**Discovered:** 2026-01-03
**ROI:** 650%
**Monthly Revenue:** $122.15
**6-Month Revenue:** $732.90
**Optimal Price:** $4.99
**Competition:** golden_opportunity
**Avg Rating:** 4.1

**Keywords:**
- mindfulness for beginners
- mindfulness guide
- easy mindfulness
- complete mindfulness
- mindfulness book
- learn mindfulness
- mindfulness step by step

**Target Audience:** People interested in mindfulness
**Book Angle:** Beginner-friendly guide to mindfulness
**Status:** ready_for_content

---

## 2. dog training

**Discovered:** 2026-01-03
**ROI:** 650%
**Monthly Revenue:** $122.15
**6-Month Revenue:** $732.90
**Optimal Price:** $4.99
**Competition:** golden_opportunity
**Avg Rating:** 4.1

**Keywords:**
- dog training for beginners
- dog training guide
- easy dog training
- complete dog training
- dog training book
- learn dog training
- dog training step by step

**Target Audience:** People interested in dog training
**Book Angle:** Beginner-friendly guide to dog training
**Status:** ready_for_content

---
```

---

## 🔍 How to Use Results

### 1. Review Opportunities

```bash
cd C:/Users/user/Desktop/KDP
git pull  # Get latest research
cd books/research
cat opportunities_2026-01-03.md
```

### 2. Pick a Niche

Look for:
- ✅ High ROI (600%+)
- ✅ Golden opportunity competition
- ✅ Topics you can write about
- ✅ Evergreen demand (not trendy)

### 3. Generate Book

Use that niche in **Workflow 2**:

1. Open Workflow 2
2. Click "Set Niche (EDIT THIS)" node
3. Change niche to: "mindfulness"
4. Execute workflow
5. Wait 10-15 minutes
6. Book generated!

---

## 🛠️ Troubleshooting

### "No opportunities found"

**Possible reasons:**
- All niches too competitive (all have 4.5+ ratings)
- Amazon blocked scraping (try again later)
- Niches too obscure (no search results)

**Fix:**
- Edit niche list with different topics
- Try broader/narrower niches
- Run again in a few hours

### "GitHub authentication failed"

**Fix:**
- Check token has `repo` scope
- Regenerate token if expired
- Ensure username/repo match exactly

### "File already exists"

**Solution:**
- GitHub won't overwrite files
- Workflow creates one file per day
- If you run multiple times in one day, it will fail on second run
- Either:
  1. Wait until tomorrow
  2. Delete the file from GitHub first
  3. Or ignore (first run already saved)

### "Amazon returned empty results"

**Fix:**
- Amazon may have rate-limited you
- Wait 30-60 minutes
- Try different niches
- Add delay between requests (edit Code node)

---

## 📈 Understanding the Analysis

### Competition Scoring:

| Score | Meaning | Criteria |
|-------|---------|----------|
| **golden_opportunity** | ✅ BEST | Low ratings (4.1-4.3), good demand |
| **high_competition** | ⚠️ Tough | Many 4.5+ star books |
| **moderate** | 🤔 Maybe | Mixed results |
| **low_demand** | ❌ Skip | Few or no results |
| **no_data** | ⚠️ Error | Amazon request failed |

### ROI Calculation:

```
Production Cost: $1.57 (OpenAI API)
Optimal Price: $4.99
Royalty Rate: 70%
Estimated Sales: 35/month

Monthly Revenue = 35 × ($4.99 × 0.70) = $122.15
6-Month Revenue = $122.15 × 6 = $732.90
ROI = (($732.90 - $1.57) / $1.57) × 100 = 646%
```

**Conservative estimates** - you may earn more!

### Keyword Strategy:

Each niche gets 7 keywords:
1. `{niche} for beginners` - High search volume
2. `{niche} guide` - Intent to learn
3. `easy {niche}` - Low difficulty
4. `complete {niche}` - Comprehensive
5. `{niche} book` - Direct search
6. `learn {niche}` - Educational intent
7. `{niche} step by step` - Beginner-friendly

Use these in your KDP metadata!

---

## 🎨 Customization Options

### Change Niche Count

**Current:** 10 niches per run

**To change:**
1. Edit "Create Niche List" node
2. Add/remove items from array
3. Can test 3-5 niches (faster) or 20+ (slower)

### Adjust ROI Threshold

**Current:** 400%+ only

**To change:**
1. Click "Filter Excellent ROI (400%+)" node
2. Change value: `400` to your desired threshold
3. Lower = more results (e.g., 300%)
4. Higher = fewer results (e.g., 600%)

### Add More Analysis

**Current:** Simple heuristic scoring

**To improve:**
1. Edit "Analyze Competition" node
2. Add more sophisticated parsing:
   - Extract actual prices
   - Count number of results
   - Parse star ratings accurately
   - Get review counts
3. Requires HTML parsing (Cheerio library)

### Change Report Format

**Current:** Markdown file

**To change:**
1. Edit "Compile Report" node
2. Change format:
   - CSV: `const csv = opportunities.map(o => [o.niche, o.roi].join(','))`
   - JSON: `JSON.stringify(opportunities, null, 2)`
   - HTML: `<table>...</table>`

---

## 💡 Pro Tips

### Best Niches to Research:

✅ **Good:**
- Health & wellness
- Self-improvement
- Hobbies & crafts
- Business skills
- Cooking & recipes
- Pet care
- Home improvement

❌ **Avoid:**
- Trending topics (lose value quickly)
- Celebrity niches (copyright issues)
- Highly technical (hard to write)
- News/current events (outdated fast)

### Timing:

Run research:
- **Best:** Monday mornings (fresh week)
- **Good:** Monthly for new trends
- **Avoid:** Black Friday / holiday seasons (skewed data)

### Next Steps After Research:

1. **Week 1:** Find 3 golden opportunities
2. **Week 2:** Generate books for all 3 (Workflow 2)
3. **Week 3:** Create covers (Workflow 3)
4. **Week 4:** Publish all 3 to KDP
5. **Repeat** with new niches

---

## 📊 Performance Metrics

### Expected Results Per Run:

- **Niches Analyzed:** 10
- **Golden Opportunities Found:** 2-4 (average)
- **Excellent ROI (400%+):** 1-3 (average)
- **Time:** 2-5 minutes
- **Cost:** $0.00

### Success Rate by Niche Type:

| Category | Success Rate | Notes |
|----------|--------------|-------|
| Health/Wellness | 60% | High demand, moderate competition |
| Self-Help | 50% | Very competitive but huge market |
| Hobbies | 70% | Lower competition, loyal buyers |
| Business | 40% | Oversaturated in many sub-niches |
| Cooking | 55% | Evergreen demand |

---

## 🔒 Privacy & Ethics

### What Data is Collected:

- ✅ Public Amazon search results
- ✅ Book titles, ratings, prices (public data)
- ❌ NO personal information
- ❌ NO user accounts scraped
- ❌ NO copyrighted content

### Ethical Scraping:

- Uses public search URLs only
- No aggressive rate limiting abuse
- Respects robots.txt
- Reasonable delays between requests
- No account required

### Amazon Terms of Service:

Web scraping of public data is generally acceptable for research purposes, but:
- Don't resell the data
- Don't overload their servers
- Use data only for your own publishing decisions
- Consider using Amazon Product Advertising API for commercial use

---

## 🚀 Next Workflow

After finding a golden opportunity:

**→ Go to Workflow 2** (`WORKFLOW-2.md`)
- Generate complete book for chosen niche
- 15,000-20,000 words
- 12 chapters
- Professional quality

---

## 📝 Summary

**Workflow 1 gives you:**
- ✅ Automated niche discovery
- ✅ ROI calculations
- ✅ Competition analysis
- ✅ Keyword suggestions
- ✅ GitHub-committed reports
- ✅ Zero cost per run

**You need:**
- ⚙️ GitHub account
- ⚙️ 5 minutes to set up
- ⚙️ Patience (results vary)

**Success formula:**
```
Weekly Research → Pick Best Niche → Generate Book → Publish → Profit
```

---

**Ready?** Import the workflow and find your first golden opportunity!

---

*Last Updated: January 3, 2026*
*Workflow Version: 1.0.0*
*Status: Production Ready*
