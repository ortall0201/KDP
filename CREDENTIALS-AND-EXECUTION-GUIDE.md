# 🔑 Required Credentials & Execution Guide

**System:** KDP Professional Automation
**Last Updated:** January 3, 2026

---

## Table of Contents

1. [Required Credentials Overview](#required-credentials-overview)
2. [Detailed Credential Setup](#detailed-credential-setup)
3. [Workflow Execution Guide](#workflow-execution-guide)
4. [Sequential vs Parallel Execution](#sequential-vs-parallel-execution)
5. [Weekly Publishing Routine](#weekly-publishing-routine)
6. [Troubleshooting](#troubleshooting)

---

## Required Credentials Overview

### **Mandatory (Must Have)**

| Service | Cost | Purpose | Used In |
|---------|------|---------|---------|
| ✅ **OpenAI API** | $50-200/mo | Book content & covers | Workflows 2, 3, 4 |
| ✅ **Google Drive** | Free | File storage | ALL workflows |
| ✅ **Google Sheets** | Free | Database | ALL workflows |
| ✅ **n8n Account** | $0-20/mo | Workflow automation | System core |

### **Recommended (Strongly Advised)**

| Service | Cost | Purpose | Used In |
|---------|------|---------|---------|
| 📱 **Slack** | Free | Notifications | Workflows 1, 2, 3, 5, 6, 7 |
| 📧 **Email SMTP** | Free | Alerts & reports | Workflows 1, 6, 7 |

### **Optional (Advanced Features)**

| Service | Cost | Purpose | Used In |
|---------|------|---------|---------|
| 💰 **Amazon SP-API** | Free | Sales analytics | Workflow 6 |
| 🎨 **Canva API** | Free-$13/mo | Promo graphics | Workflow 7 |
| 🐦 **Twitter API** | Free | Marketing | Workflow 5 |
| 📘 **Facebook API** | Free | Marketing | Workflow 5 |

---

## Detailed Credential Setup

### 1. **OpenAI API** ⚡ REQUIRED

**Why you need it:**
- Generates book content (15,000-20,000 words)
- Creates book covers (DALL-E 3)
- Optimizes metadata (titles, keywords, descriptions)

**How to get it:**

1. Go to https://platform.openai.com/signup
2. Create account
3. Add payment method
4. Go to https://platform.openai.com/api-keys
5. Click "Create new secret key"
6. Copy key (starts with `sk-proj-...`)
7. Add $20 initial credit (recommended)

**Cost:**
- GPT-4 Turbo: $0.01/1K input, $0.03/1K output
- DALL-E 3: $0.04-0.08/image
- Average: $1.57 per complete book

**In n8n:**
1. Go to Credentials → Add Credential
2. Search "OpenAI"
3. Select "OpenAI API"
4. Paste your API key
5. Click "Save"

**Used in:**
- Workflow 2: Content Production (GPT-4)
- Workflow 3: Cover Design (DALL-E 3)
- Workflow 4: Metadata Optimization (GPT-4)

---

### 2. **Google Drive & Sheets** 📁 REQUIRED

**Why you need it:**
- Stores manuscripts and covers
- Database for opportunities, books, analytics
- Free unlimited storage (for your needs)

**How to get it:**

1. You need a Google account (Gmail)
2. In n8n, credentials use OAuth2 (automatic)
3. Just click "Connect" and authorize

**Required Google Sheets Structure:**

Create ONE spreadsheet with 4 tabs:

#### **Tab 1: "Opportunities"**
```
Columns:
Date | Niche | Optimal_Price | Monthly_Revenue | Six_Month_Revenue |
ROI_Percentage | Competition | Avg_Rating | Recommendation | Keywords |
Target_Audience | Book_Angle | Status
```

#### **Tab 2: "Books"**
```
Columns:
Book_ID | Title | Niche | Word_Count | Chapters | Price | Keywords |
Manuscript_URL | Cover_URL | Status | Generated_Date
```

#### **Tab 3: "ReadyToPublish"**
```
Columns:
Book_ID | Full_Title | Description | Keywords | Categories | Price |
Manuscript_URL | Cover_URL | Metadata_Doc_URL | Published_Date |
Amazon_Link | ASIN
```

#### **Tab 4: "Analytics"**
```
Columns:
Date | Book_ID | Title | Units_Sold | Revenue | Royalty | Page_Views |
Sessions | Conversion_Rate | BSR | Performance | Monthly_Projection
```

**Required Google Drive Folders:**

Create these folders in your Drive:
- `KDP Manuscripts`
- `KDP Covers`
- `KDP Metadata`

**In n8n:**
1. Add credential: "Google Sheets OAuth2 API"
2. Click "Connect with Google"
3. Authorize n8n access
4. Repeat for "Google Drive OAuth2 API"

**Get Sheet ID:**
- Open your Google Sheet
- Look at URL: `https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit`
- Copy `YOUR_SHEET_ID`
- Paste in workflow JSON files (replace `YOUR_SHEET_ID`)

**Get Folder ID:**
- Open folder in Drive
- Look at URL: `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`
- Copy `YOUR_FOLDER_ID`
- Paste in workflow JSON files (replace `YOUR_FOLDER_ID`)

**Used in:**
- ALL workflows (1-7)

---

### 3. **Slack** 📱 RECOMMENDED

**Why you need it:**
- Real-time alerts for hot niches
- Notifications when books are ready
- Performance alerts
- Daily summaries

**How to get it:**

1. Go to https://slack.com/create
2. Create free workspace
3. Create channels:
   - `#kdp-opportunities` - Niche research alerts
   - `#kdp-production` - Content/cover ready
   - `#kdp-marketing` - Marketing updates
   - `#kdp-dashboard` - Daily summaries
   - `#kdp-alerts` - Performance warnings
   - `#kdp-wins` - Success celebrations

**Option A: Webhook (Easiest)**

1. Go to https://api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name: "KDP Automation"
5. Select your workspace
6. Click "Incoming Webhooks"
7. Activate webhooks
8. Click "Add New Webhook to Workspace"
9. Select channel (#kdp-opportunities)
10. Copy webhook URL
11. Repeat for each channel

**Option B: Bot Token (Advanced)**

1. Create app (same as above)
2. Go to "OAuth & Permissions"
3. Add scopes: `chat:write`, `chat:write.public`
4. Install app to workspace
5. Copy "Bot User OAuth Token"

**In n8n:**
1. Add credential: "Slack API"
2. Choose "Access Token"
3. Paste your webhook URL or token
4. Save

**Cost:** Free forever

**Used in:**
- Workflow 1: Hot niche alerts
- Workflow 2: Content ready notifications
- Workflow 3: Cover ready alerts
- Workflow 5: Marketing updates
- Workflow 6: Daily analytics
- Workflow 7: Pricing recommendations

---

### 4. **Email SMTP** 📧 RECOMMENDED

**Why you need it:**
- Email notifications for opportunities
- Daily performance reports
- Weekly optimization plans

**Options:**

#### **Option A: Gmail (Free)**

1. Enable 2FA on Gmail
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and your device
4. Generate password
5. Copy 16-character password

**In n8n:**
- Host: `smtp.gmail.com`
- Port: `587`
- Username: your Gmail address
- Password: app password (not regular password)

#### **Option B: SendGrid (100 emails/day free)**

1. Sign up at https://sendgrid.com
2. Create API key
3. Copy key

**In n8n:**
- Add credential: "SendGrid API"
- Paste API key

#### **Option C: Mailchimp (Free tier)**

1. Sign up at https://mailchimp.com
2. Get API key from account settings
3. Used for marketing emails

**Cost:** Free tier sufficient

**Used in:**
- Workflow 1: Opportunity alerts
- Workflow 5: Email marketing campaigns
- Workflow 6: Daily reports
- Workflow 7: Weekly recommendations

---

### 5. **Amazon SP-API** 💰 OPTIONAL (Advanced)

**Why you need it:**
- Automatic sales data retrieval
- Real-time BSR tracking
- Revenue analytics

**How to get it:**

1. Go to Seller Central
2. Navigate to "Apps & Services"
3. Register as developer
4. Create app credentials
5. Wait 1-2 days for approval

**Note:** Can skip initially. Add later when you have 20+ books.

**In n8n:**
- Complex OAuth2 setup
- Follow Amazon documentation
- Or use manual data entry initially

**Cost:** Free

**Used in:**
- Workflow 6: Sales analytics

---

### 6. **n8n Account** 🤖 REQUIRED

**Why you need it:**
- Runs all automation workflows
- Connects all services together
- Heart of the system

**Option A: n8n Cloud (Recommended for Beginners)**

1. Go to https://n8n.cloud
2. Sign up (14-day free trial)
3. Create workspace
4. Import workflows

**Cost:** $20/month after trial

**Pros:**
- No setup required
- Always online
- Automatic updates
- No technical knowledge needed

**Option B: Self-Hosted (For Advanced Users)**

```bash
# Docker (easiest self-host)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Then open: http://localhost:5678
```

**Cost:** Free (or $5-10/month VPS)

**Pros:**
- Free forever
- Complete control
- No monthly fees

**Cons:**
- Requires Docker knowledge
- Must keep computer/server running
- You handle updates

---

## Workflow Execution Guide

### **Understanding the 7 Workflows**

#### **✅ Available as JSON (Ready to Import)**

1. **Niche Research Engine** - `1-kdp-niche-research-engine.json`
2. **Content Production Pipeline** - `2-kdp-content-production-pipeline.json`
3. **Cover Design Automation** - `3-kdp-cover-design-automation.json`

#### **📝 Available as Templates (Build or Request JSON)**

4. **Metadata Optimization** - Documented in system guide
5. **Marketing Automation** - Documented in system guide
6. **Analytics & Tracking** - Documented in system guide
7. **Income Optimization** - Documented in system guide

---

### **Why Only 3 JSON Files?**

**Short Answer:** Response size limitations + modular approach

**Detailed Explanation:**

**1. Core vs Optional**
- Workflows 1-3 are **ESSENTIAL** - You need these to publish books
- Workflows 4-7 are **OPTIMIZATION** - Nice to have, but not required to start

**2. Response Limitations**
- Each workflow JSON is 10-20 KB
- Full 7 workflows would be 100+ KB of code
- Claude responses have size limits

**3. Modular Approach**
- Start with 3 core workflows
- Get profitable first
- Add optimization workflows later as you scale

**4. Templates Provided**
- Workflows 4-7 are fully documented
- You can build them manually in n8n (30 min each)
- OR request individual JSON files: "Create workflow 4 JSON"

**5. Flexibility**
- Not everyone needs all 7 workflows
- Some prefer Zapier for marketing
- Some use manual analytics initially
- Templates let you customize

---

### **What Each Workflow Does**

| # | Name | Purpose | When to Use |
|---|------|---------|-------------|
| 1 | Niche Research | Find profitable opportunities | Every 3 days (auto) |
| 2 | Content Production | Generate complete books | When you want a new book |
| 3 | Cover Design | Create professional covers | After content is ready |
| 4 | Metadata | Optimize for Amazon SEO | Before KDP upload |
| 5 | Marketing | Multi-channel promotion | After book goes live |
| 6 | Analytics | Track performance | Daily (auto) |
| 7 | Optimization | Maximize revenue | Weekly (auto) |

---

## Sequential vs Parallel Execution

### **Sequential Execution** (One After Another)

**Required for:**
- Workflow 2 → Workflow 3 (same book)
  - Content MUST finish before cover
  - Cover needs book data from content workflow

**Recommended for:**
- Multiple Workflow 2 runs (different books)
  - Avoids confusion
  - Easier to track
  - Saves OpenAI costs (reduces rate limits)

**Timeline Example:**
```
9:00 AM: Start Workflow 2 (Book A)
9:15 AM: Workflow 3 auto-triggers (Book A cover)
9:20 AM: Start Workflow 2 (Book B)
9:35 AM: Workflow 3 auto-triggers (Book B cover)
```

---

### **Parallel Execution** (Simultaneously)

**Safe to run together:**
- Workflow 1 (Research) + Workflow 2 (Content) ✅
- Workflow 1 (Research) + Workflow 6 (Analytics) ✅
- Workflow 5 (Marketing) + Workflow 1 (Research) ✅
- Workflow 6 (Analytics) + Workflow 7 (Optimization) ✅

**Do NOT run together:**
- Multiple Workflow 2 instances ❌ (expensive + confusing)
- Workflow 2 + Workflow 3 (same book) ❌ (sequential required)

---

### **Execution Decision Tree**

```
Want to create a book?
└─> Run Workflow 2 (Content)
    └─> Wait 10-15 minutes
        └─> Workflow 3 auto-runs (Cover)
            └─> Wait 2-3 minutes
                └─> Download files, review quality

Need to find niches?
└─> Workflow 1 runs automatically every 3 days
    └─> Check Slack/#kdp-opportunities for alerts
        └─> Check Google Sheets for details

Book published on KDP?
└─> Trigger Workflow 5 (Marketing) via webhook
    └─> Runs immediately
        └─> Posts to all channels

Want performance data?
└─> Workflow 6 runs daily at 6 AM (automatic)
    └─> Check email for daily report
```

---

## Weekly Publishing Routine

### **Monday: Research & Plan** 🔍

**Morning (30 min)**
```
□ Check Slack #kdp-opportunities channel
□ Review Google Sheets "Opportunities" tab
□ Select 2-3 profitable niches for the week
□ Mark as "ready_for_content" in Sheets
```

**Afternoon (2 hours)**
```
□ 2:00 PM: Trigger Workflow 2 for Book A
□ 2:15 PM: Wait for completion (check Slack)
□ 2:30 PM: Workflow 3 auto-runs (cover)
□ 2:35 PM: Download & review Book A files
□ 3:00 PM: Trigger Workflow 2 for Book B
□ 3:30 PM: Download & review Book B files
```

---

### **Tuesday: Metadata & Polish** ✨

**Morning (1 hour)**
```
□ Review Book A content quality
□ Minor edits if needed
□ Run Workflow 4 (Metadata) for Book A
□ Same for Book B
□ Download metadata documents
```

**Afternoon (1 hour)**
```
□ Prepare KDP upload checklist
□ Organize files in folders
□ Create upload schedule
```

---

### **Wednesday: KDP Upload Day** 📤

**Morning (1.5 hours)**
```
□ Log into KDP dashboard
□ Upload Book A:
  - Manuscript (from Drive)
  - Cover (from Drive)
  - Metadata (from document)
  - ✅ CHECK AI DISCLOSURE BOX
  - Set price
  - Preview on all devices
  - Publish
□ Time: 30 minutes per book
```

**Afternoon (1.5 hours)**
```
□ Upload Book B
□ Upload Book C (if ready)
□ Update Google Sheets with ASIN
```

---

### **Thursday: Marketing Prep** 📱

**Morning (30 min)**
```
□ Check if books went live (12-72 hours)
□ If live: Trigger Workflow 5 (Marketing)
□ Verify social posts went out
□ Check email campaign sent
```

**Afternoon (30 min)**
```
□ Manual social media engagement
□ Respond to any early questions
□ Share in relevant groups/forums
```

---

### **Friday: Analytics Review** 📊

**Morning (30 min)**
```
□ Check Workflow 6 daily report (email)
□ Review Google Sheets "Analytics" tab
□ Note any immediate issues
□ Celebrate wins in #kdp-wins channel
```

**Afternoon (30 min)**
```
□ Plan next week's niches
□ Adjust strategy based on data
□ Update pricing if needed
```

---

### **Weekend: Optimization** 💰

**Sunday Morning (30 min)**
```
□ Review Workflow 7 weekly optimization report
□ Implement pricing changes in KDP dashboard
□ Schedule promotional campaigns
□ Plan next week's content topics
```

---

## Execution Best Practices

### **DO These Things** ✅

1. **Run Workflow 1 on schedule (auto)**
   - Let it find niches every 3 days
   - Check Slack for hot opportunities

2. **Wait for Workflow 2 to complete**
   - 10-15 minutes per book
   - Don't interrupt or run multiple simultaneously

3. **Let Workflow 3 auto-trigger**
   - Configured to run after Workflow 2
   - Or trigger manually if needed

4. **Review content quality**
   - Always check before publishing
   - Make minor edits if needed
   - Ensure value for readers

5. **Check AI disclosure box** ⚠️ CRITICAL
   - MANDATORY per 2026 Amazon policies
   - Can get account suspended if skipped

6. **Track everything**
   - Use Google Sheets religiously
   - Monitor analytics daily
   - Adjust based on data

---

### **DON'T Do These Things** ❌

1. **Don't run multiple Workflow 2 instances together**
   - Expensive (2× OpenAI costs)
   - Confusing (which book is which?)
   - Can hit rate limits

2. **Don't skip quality review**
   - AI content needs human oversight
   - 10 minutes review = better reviews

3. **Don't forget AI disclosure**
   - Amazon WILL catch it
   - Account penalties
   - Book removal

4. **Don't publish without previewing**
   - Check on all devices
   - Verify formatting
   - Test links

5. **Don't ignore analytics**
   - Data tells you what's working
   - Kill losers (<$20/mo after 3 months)
   - Double down on winners

---

## Troubleshooting

### **Workflow 1: Niche Research**

**Issue:** No results found
**Solution:**
- Check niche seeds in workflow
- Verify internet connection
- Check Google Sheets permissions

**Issue:** All niches marked "poor"
**Solution:**
- This is normal! System filters heavily
- Run for 2 weeks to find golden opportunities
- Lower ROI threshold in code if needed

---

### **Workflow 2: Content Production**

**Issue:** Workflow times out
**Solution:**
- Increase n8n timeout (Settings > Executions > Timeout)
- Default is 2 min, set to 20 minutes
- Or use webhook-based workflows

**Issue:** Content quality is poor
**Solution:**
- Review prompts in workflow
- Increase temperature for creativity
- Use better niche descriptions
- Add human editing step

**Issue:** OpenAI quota exceeded
**Solution:**
- Check usage at platform.openai.com
- Add more credits
- Upgrade to higher tier
- Wait for monthly reset

---

### **Workflow 3: Cover Design**

**Issue:** Covers don't match genre
**Solution:**
- Customize prompts in "Generate Cover Prompt" node
- Add more specific genre keywords
- Test different DALL-E prompts

**Issue:** Wrong dimensions
**Solution:**
- Verify "Resize for KDP" node settings
- Should be 1600×2560 (portrait)
- Or 2560×1600 (landscape)

---

### **Common n8n Issues**

**Issue:** "Credentials not found"
**Solution:**
- Re-add credential in n8n
- Test connection
- Check API key is correct

**Issue:** "Sheet ID not found"
**Solution:**
- Verify Sheet ID in URL
- Check sharing permissions (Anyone with link can edit)
- Ensure correct sheet name

**Issue:** "Workflow not triggering"
**Solution:**
- Check workflow is activated (toggle in top right)
- Verify trigger settings (schedule/webhook)
- Check execution history for errors

---

## Quick Reference

### **Credential Summary**

| Service | Cost | Setup Time | Difficulty |
|---------|------|------------|------------|
| OpenAI | $50-200/mo | 5 min | Easy |
| Google | Free | 10 min | Easy |
| Slack | Free | 15 min | Easy |
| Email | Free | 10 min | Easy |
| n8n | $0-20/mo | 5 min | Easy |
| Amazon SP-API | Free | 2 days | Hard |

**Total setup time: 45 minutes** (excluding Amazon SP-API)

---

### **Execution Summary**

| Workflow | Trigger | Frequency | Can Run With |
|----------|---------|-----------|--------------|
| 1. Research | Schedule | Every 3 days | Everything |
| 2. Content | Manual | On-demand | Only 1, 6, 7 |
| 3. Cover | Auto/Manual | After content | Everything except 2 |
| 4. Metadata | Manual | Before publish | Everything |
| 5. Marketing | Webhook | After live | Everything |
| 6. Analytics | Schedule | Daily 6 AM | Everything |
| 7. Optimization | Schedule | Weekly Sunday | Everything |

---

### **Weekly Time Investment**

| Activity | Time | Frequency |
|----------|------|-----------|
| Check opportunities | 15 min | Daily |
| Trigger content workflows | 10 min | 2-3×/week |
| Review & edit content | 30 min | Per book |
| KDP manual upload | 30 min | Per book |
| Marketing follow-up | 15 min | Daily |
| Analytics review | 15 min | Daily |

**Total: 2-4 hours/week for 2-3 books**

---

## Next Steps

### **Phase 1: Setup (Today)**
1. ✅ Read this guide completely
2. ✅ Sign up for n8n
3. ✅ Get OpenAI API key
4. ✅ Create Google Sheet & folders
5. ✅ Set up Slack (optional)

### **Phase 2: Import (Tomorrow)**
1. ✅ Import Workflow 1
2. ✅ Add all credentials
3. ✅ Update Sheet/Folder IDs
4. ✅ Test niche research
5. ✅ Verify data in Sheets

### **Phase 3: First Book (This Week)**
1. ✅ Import Workflow 2
2. ✅ Import Workflow 3
3. ✅ Generate first book
4. ✅ Review quality
5. ✅ Publish to KDP

### **Phase 4: Scale (This Month)**
1. ✅ Publish 3-5 books
2. ✅ Set up marketing (Workflow 5)
3. ✅ Enable analytics (Workflow 6)
4. ✅ Monitor performance
5. ✅ Optimize based on data

---

## Getting Additional Workflows

**Need Workflows 4-7 as JSON?**

Just ask:
```
"Create workflow 4 JSON file"
"Generate metadata optimization workflow"
"Build marketing automation JSON"
"Create analytics workflow JSON"
```

I'll create them individually on request!

---

**Next:** Open `START-HERE.md` to begin your journey!

Or use `/kdp` in Claude Code for instant help!

---

*Last Updated: January 3, 2026*
*System Version: 1.0.0*
