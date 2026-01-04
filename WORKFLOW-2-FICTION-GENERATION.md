# Workflow 2: Fiction Content Generation

## Overview

Generates complete 18,000-word fiction manuscripts based on best seller patterns from Workflow 1. Uses GPT-4 to create compelling stories that mimic successful books in your chosen genre.

## What This Workflow Does

1. **Takes your book concept** (based on best sellers you researched)
2. **Generates a detailed story outline**:
   - Main characters (names, motivations, conflicts)
   - Setting (world, locations, time period)
   - Plot structure (opening, climax, resolution)
   - Chapter breakdown
   - Key themes and emotional beats
3. **Writes 10 chapters** (~1,800-2,000 words each)
4. **Compiles the manuscript** with proper formatting
5. **Saves to GitHub** for version control

## Target Output

- **Word Count:** 18,000-20,000 words
- **Chapters:** 10 chapters with strong narrative flow
- **Style:** Commercial fiction matching bestseller tone
- **Format:** Ready for Upwork editor to polish

## How to Use

### Step 1: Research Best Sellers First

Before using this workflow, run **Workflow 1** to see what's selling:
- What themes are hot? (Romantasy, Mafia Romance, etc.)
- What title patterns work?
- What's the average rating/reviews?

### Step 2: Create Your Book Concept

Based on Workflow 1 research, create a concept that mimics best sellers.

**Example from Romance research:**
- Best seller: "Quicksilver (Fae & Alchemy Book 1)" - 212K reviews
- Your concept: "Romantasy: A forbidden romance between a mortal alchemist and a dangerous Fae prince in a world where magic and science collide"

**More examples:**

**If researching Billionaire Romance:**
- Best seller pattern: Powerful CEO + struggling artist
- Your concept: "A ruthless tech billionaire falls for the coffee shop owner who refuses to sell her building to his company"

**If researching Thriller:**
- Best seller pattern: Domestic suspense with unreliable narrator
- Your concept: "A woman wakes up in a stranger's home with no memory of the past week and evidence suggesting she committed a crime"

**If researching LitRPG:**
- Best seller pattern: Gamer trapped in virtual world
- Your concept: "A beta tester gets trapped in an AI-powered fantasy game where dying means permanent deletion of his consciousness"

### Step 3: Configure the Workflow

1. **Import** `2-kdp-fiction-SIMPLE-WORKING.json` into n8n (this is the FIXED version)
2. **Open** the "Set Book Concept" node
3. **Edit these fields:**
   - `book_concept`: Your story concept (be specific and detailed)
   - `genre`: The fiction category (Romance, Thriller, Fantasy, etc.)
   - `target_words`: 18000 (adjust if needed, min 15000, max 25000)
4. **Configure** GitHub credentials in the "Commit to GitHub" node
   - Select your GitHub owner (username)
   - Select your repository name
5. **Save** the workflow

### Step 4: Execute

1. Click **Execute Workflow** (manual trigger)
2. Wait **15-20 minutes** (GPT-4 generates 10 chapters sequentially)
3. Check `books/manuscripts/` in your GitHub repo for the completed manuscript

### Step 5: Review Output

The manuscript includes:
- Copyright notice
- Warning that it's AI-generated and needs editing
- Next steps reminder
- 10 complete chapters
- Word count statistics

## Example Book Concepts by Genre

### Romance / Romantasy
```
Concept: A forbidden romance between a mortal alchemist and a dangerous Fae prince in a world where magic and science collide

Genre: Romance/Fantasy (Romantasy)
```

### Billionaire Romance
```
Concept: When a small-town bakery owner refuses to sell to a ruthless real estate mogul, he offers her a deal: one month as his fake girlfriend to impress his family, and he'll drop the purchase. She agrees, not knowing he's hiding a devastating secret.

Genre: Contemporary Romance
```

### Mafia Romance
```
Concept: An undercover FBI agent must marry the heir to a crime family to infiltrate them, but she never expected to fall for the man she's sworn to destroy.

Genre: Mafia Romance
```

### Thriller
```
Concept: A therapist realizes her new patient is describing crimes that match unsolved murders in the area. But when she reports it, evidence points to her as the killer instead.

Genre: Psychological Thriller
```

### Fantasy
```
Concept: In a world where dreams are harvested as currency, a nightmare thief discovers she's stealing memories of a war that was erased from history.

Genre: Urban Fantasy
```

### LitRPG
```
Concept: A dying gamer uploads his consciousness into an experimental MMORPG as a last resort, only to discover the game's AI has enslaved the minds of thousands of players before him.

Genre: LitRPG / GameLit
```

## Prompt Engineering Tips

The workflow uses carefully crafted prompts:

### For the Outline (Step 1):
- Asks for **compelling, commercial** content
- Requests **character depth** (motivations, conflicts)
- Demands **emotional beats** (what readers should feel)
- Uses "This should feel like a bestseller"

### For Each Chapter (Step 2):
- Temperature set to **0.9** (more creative, less predictable)
- "Show, don't tell" instruction
- Emphasis on **dialogue and sensory details**
- "Page-turning" and "compelling" keywords
- Chapter-ending hooks to keep readers engaged

## Cost Estimate

**Per book:**
- Story outline: ~$0.10 (3,000 tokens)
- 10 chapters: ~$2.00 (35,000 tokens total)
- **Total AI cost: ~$2.10**

**Plus Upwork editor:**
- Budget: $50-$200 depending on editing depth
- **Total per book: $52-$202**

## What to Send to Your Upwork Editor

When posting the job, provide:
1. The complete manuscript (from GitHub)
2. The story outline (included in output)
3. Instructions:
   - Improve dialogue naturalness
   - Enhance character depth and emotions
   - Fix pacing issues
   - Add sensory details where missing
   - Ensure consistent voice
   - Catch continuity errors
   - Make it "feel" human-written

**Sample Upwork job post:**
```
Title: Edit and Polish AI-Generated Fiction Manuscript

I have an 18,000-word [GENRE] manuscript that was generated with AI. It has a solid plot and structure, but needs human polish to make it publication-ready.

Your tasks:
- Improve dialogue to sound natural
- Deepen character emotions and motivations
- Enhance sensory descriptions
- Fix any pacing issues
- Ensure consistent voice throughout
- Catch continuity errors
- Make it read like a human wrote it

Deliverable: Edited manuscript in .docx format
Timeline: 5-7 days
Budget: $[50-200] (specify your rate per word or flat rate)

Please provide samples of fiction editing work.
```

## Workflow Settings

**Model:** GPT-4 Turbo Preview
- Best balance of quality and cost
- Strong narrative ability
- Good at emotional depth

**Temperature:**
- Outline: 0.8 (structured but creative)
- Chapters: 0.9 (more creative and varied)

**Max Tokens:**
- Outline: 3,000 tokens
- Chapters: 3,500 tokens each

**Chapters:** 10 (adjustable)
- Edit the `chapters` array in "Store Outline" node
- Example for 12 chapters: `[1,2,3,4,5,6,7,8,9,10,11,12]`

## Troubleshooting

### Chapters feel repetitive
- Increase temperature to 0.95
- Add more specific details to your concept
- Make outline more detailed before chapter generation

### Output is too short
- Increase `max_tokens` to 4000
- Add "minimum 2,000 words" to chapter prompt
- Increase chapter count to 12

### Output is too generic
- Be MORE specific in your book concept
- Add character names, specific settings, unique hooks
- Reference specific best sellers to mimic

### Workflow times out
- Chapter generation takes ~90 seconds each
- 10 chapters = ~15 minutes total
- Increase n8n workflow timeout if needed

## Next Steps After Generation

1. ✅ **Review manuscript** - Read through, note major issues
2. ✅ **Post Upwork job** - Hire editor to polish
3. ✅ **Review edited version** - Approve final draft
4. ✅ **Generate cover** - Use Workflow 3
5. ✅ **Publish on KDP** - Check AI disclosure box
6. ✅ **Launch free** - Get reviews first
7. ✅ **Add price** - After 10-20 reviews

## Tips from the 10-Year Publisher

- **Don't try to be original** - Mimic what's selling
- **Series beat single books** - Plan trilogy from start
- **Launch Book 1 free** - Hook readers, sell Books 2-3
- **Human editing is non-negotiable** - AI needs polish
- **Title matters** - Use bestseller patterns
- **Cover matters** - Mimic bestseller styles (Workflow 3)

## Files

### Workflow Files:
- **USE THIS:** `2-kdp-fiction-SIMPLE-WORKING.json` - FIXED version that processes all 10 chapters correctly
- **OLD (broken):** `2-kdp-fiction-content-generation.json` - Only processes 1 chapter, DO NOT USE
- **OLD (broken):** `2-kdp-fiction-content-generation-FIXED.json` - Attempted fix, still broken

### Input/Output:
- **Input:** Your book concept (edit in "Set Book Concept" node)
- **Output:** `books/manuscripts/[timestamp]_fiction.txt`
- **Includes:** Full manuscript with all 10 chapters

---

**This workflow implements the proven strategy of a 10+ year KDP publisher. Use it to generate fiction fast, then polish with human expertise.**
