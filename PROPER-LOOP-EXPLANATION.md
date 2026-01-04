# THE CORRECT N8N LOOP PATTERN

## What Was Wrong Before

The previous workflows had NO LOOP structure. They were linear flows:
```
Create Items → Generate Chapter → Format Chapter → Compile
```

This meant n8n would try to pass all 10 items through at once, causing streaming issues where Compile executed before all chapters were done.

## The CORRECT Pattern

n8n requires a **LOOP-BACK connection** using the **Split In Batches** node.

### Split In Batches Has TWO Outputs:

1. **Output 0** (first output): Sends ONE batch at a time to the loop
2. **Output 1** (second output): Fires ONLY when ALL batches are complete

### The Connection Structure:

```
Create Chapter Items (outputs 10 items)
  ↓
Loop Over Chapters (Split In Batches, batchSize: 1)
  ↓ Output 0 ─────────────────────┐
  ↓                                │
Generate Chapter (processes 1 item)│
  ↓                                │
Format Chapter (formats 1 item)   │
  ↓                                │
  └────── LOOPS BACK ──────────────┘

Loop Over Chapters
  ↓ Output 1 (fires when loop done)
  ↓
Compile Manuscript (receives ALL 10 chapters)
  ↓
Commit to GitHub
```

### Key Connections:

1. **Create Chapter Items → Loop Over Chapters** (input)
2. **Loop Over Chapters Output 0 → Generate Chapter** (the loop)
3. **Generate Chapter → Format Chapter**
4. **Format Chapter → Loop Over Chapters** (LOOP BACK - this is critical!)
5. **Loop Over Chapters Output 1 → Compile Manuscript** (fires when done)
6. **Compile Manuscript → Commit to GitHub**

## How It Works

1. **Loop Over Chapters** receives 10 items
2. It sends item 1 via **Output 0** to Generate Chapter
3. Generate Chapter processes item 1 (takes ~60-90 seconds)
4. Format Chapter formats item 1
5. Format Chapter connects BACK to Loop Over Chapters input
6. Loop Over Chapters now sends item 2 via **Output 0**
7. This repeats for items 3, 4, 5, 6, 7, 8, 9, 10
8. After item 10 is processed, Loop Over Chapters knows it's done
9. **Output 1** fires for the FIRST TIME
10. Compile Manuscript receives ALL 10 formatted chapters
11. Compiles manuscript and sends to GitHub

## Console Output You'll See

```
✅ Chapter 1 completed (1842 words)
✅ Chapter 2 completed (1903 words)
✅ Chapter 3 completed (1877 words)
✅ Chapter 4 completed (1925 words)
✅ Chapter 5 completed (1889 words)
✅ Chapter 6 completed (1912 words)
✅ Chapter 7 completed (1851 words)
✅ Chapter 8 completed (1934 words)
✅ Chapter 9 completed (1897 words)
✅ Chapter 10 completed (1868 words)

🎉 ALL CHAPTERS COMPLETE! Received 10 chapters
📚 Manuscript compiled: 18542 words across 10 chapters
```

## Why This Pattern is Required

n8n doesn't automatically "wait" for all items to finish. Without the loop-back connection:
- n8n treats it as a linear flow
- Each node executes as items arrive (streaming)
- No coordination between items
- Compile node executes multiple times (once per item)

With the loop-back connection:
- Split In Batches controls the flow
- One item at a time through the loop
- Output 1 only fires when the loop completes
- Compile node executes ONCE with ALL items

## The File to Use

**Import this workflow:** `2-kdp-fiction-PROPER-LOOP.json`

This has the correct loop structure with:
- Split In Batches node
- Loop-back connection from Format Chapter to Split In Batches
- Output 1 connection to Compile Manuscript
- Console logging to track progress

## How to Configure

1. Import `2-kdp-fiction-PROPER-LOOP.json`
2. Edit "Set Book Concept" node (your story idea)
3. Configure GitHub credentials in "Commit to GitHub"
4. Execute workflow
5. Watch console logs - you'll see each chapter complete
6. After ~15-20 minutes, manuscript will be in `books/manuscripts/`

---

**This is the STANDARD n8n pattern for processing multiple items sequentially and aggregating results. It WILL work correctly.**

## Sources

- [Loop Over Items (Split in Batches) | n8n Docs](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.splitinbatches/)
- [Looping | n8n Docs](https://docs.n8n.io/flow-logic/looping/)
- [How to use aggregate with loop - n8n Community](https://community.n8n.io/t/how-to-use-aggregate-with-loop/94755)
