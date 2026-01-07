# -*- coding: utf-8 -*-
import json

with open('2026-01-06T03-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find and fix the "Split Manuscript into Chapters" node
split_node = next(n for n in workflow['nodes'] if n['name'] == 'Split Manuscript into Chapters')

# Updated code that properly extracts chapters
split_node['parameters']['jsCode'] = '''// Split manuscript into individual chapters for analysis
const manuscript = $('Decode Manuscript').first().json.data;
const config = $('Configuration').first().json;

// Find all chapter markers with their positions
const chapterRegex = /CHAPTER (\d+)/gi;
const matches = [];
let match;

while ((match = chapterRegex.exec(manuscript)) !== null) {
    matches.push({
        chapterNumber: parseInt(match[1]),
        position: match.index,
        fullMatch: match[0]
    });
}

console.log(`ℹ️  Found ${matches.length} chapter markers`);

if (matches.length === 0) {
    throw new Error('No CHAPTER markers found in manuscript. Make sure chapters are labeled "CHAPTER 1", "CHAPTER 2", etc.');
}

// Extract chapter text between markers
const chapterItems = [];

for (let i = 0; i < matches.length; i++) {
    const currentMatch = matches[i];
    const nextMatch = matches[i + 1];

    // Extract text from current chapter marker to next chapter marker (or end of manuscript)
    const startPos = currentMatch.position + currentMatch.fullMatch.length;
    const endPos = nextMatch ? nextMatch.position : manuscript.length;

    const chapterText = manuscript.substring(startPos, endPos).trim();
    const wordCount = chapterText.split(/\\s+/).filter(w => w.length > 0).length;

    console.log(`   Chapter ${currentMatch.chapterNumber}: ${wordCount} words`);

    // Only include if it has substantial content (> 100 words)
    if (wordCount > 100) {
        chapterItems.push({
            json: {
                chapter_number: currentMatch.chapterNumber,
                chapter_text: chapterText,
                word_count: wordCount,
                known_issues: config.known_issues,
                target_word_count: config.target_word_count,
                total_chapters: matches.length,
                accumulated_analyses: []
            }
        });
    } else {
        console.log(`   ⚠️  Chapter ${currentMatch.chapterNumber} too short, skipping`);
    }
}

console.log(`\\nℹ️  Split into ${chapterItems.length} valid chapters`);

return chapterItems;'''

# Save
with open('2026-01-06T03-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Fixed chapter splitting:')
print('- Now extracts text BETWEEN chapter markers')
print('- Skips preamble/header (text before first chapter)')
print('- Only includes chapters with > 100 words')
print('- Properly identifies chapter boundaries')
print('')
print('File updated: 2026-01-06T03-00-00_workflow-3-ghostwriter-LOOP-FIXED.json')
