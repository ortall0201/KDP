# -*- coding: utf-8 -*-
import json

with open('2026-01-06T10-38-27_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Remove the accumulated_analyses pattern from Split node - it doesn't work in n8n loops
split_node = next(n for n in workflow['nodes'] if n['name'] == 'Split Manuscript into Chapters')
split_node['parameters']['jsCode'] = split_node['parameters']['jsCode'].replace(
    'accumulated_analyses: []',
    '// No accumulation needed here'
)

# Update Store Chapter Analysis to just output the analysis (no accumulation)
store_node = next(n for n in workflow['nodes'] if n['name'] == 'Store Chapter Analysis')
store_node['parameters']['jsCode'] = '''// Store the analysis for this chapter
const response = $input.first().json;
const loopItem = $('PHASE 1: Chapter Analysis Loop').item.json;
const chapterNumber = loopItem.chapter_number;

// Extract analysis
const analysisText = response.choices[0].message.content;

let chapterAnalysis;
try {
    const jsonMatch = analysisText.match(/```json\\n([\\\\s\\\\S]*?)\\n```/) || analysisText.match(/```\\n([\\\\s\\\\S]*?)\\n```/);
    if (jsonMatch) {
        chapterAnalysis = JSON.parse(jsonMatch[1]);
    } else {
        chapterAnalysis = JSON.parse(analysisText);
    }
} catch (e) {
    chapterAnalysis = {
        chapter: chapterNumber,
        raw_analysis: analysisText
    };
}

console.log(`ℹ️  Analyzed Chapter ${chapterNumber}`);

// Just output this chapter's analysis - Compile will use $input.all()
return {
    json: {
        chapter_number: chapterNumber,
        analysis: chapterAnalysis,
        word_count: loopItem.word_count || 0,
        tokens_used: response.usage?.total_tokens || 0
    }
};'''

# Fix connections: Store should connect BOTH to rate limit AND to Compile
workflow['connections']['Store Chapter Analysis'] = {
    'main': [
        [
            {'node': 'Rate Limit Pause Chapter Analysis', 'type': 'main', 'index': 0},
            {'node': 'Compile All Chapter Analyses', 'type': 'main', 'index': 0}
        ]
    ]
}

# Remove the connection from Loop to Compile (we'll use Store's output instead)
if 'PHASE 1: Chapter Analysis Loop' in workflow['connections']:
    loop_connections = workflow['connections']['PHASE 1: Chapter Analysis Loop']['main']
    # Keep only output 0 (during iteration)
    workflow['connections']['PHASE 1: Chapter Analysis Loop'] = {
        'main': [
            loop_connections[0]  # Build Chapter Analysis Request
        ]
    }

# Update Compile to use $input.all() from Store Chapter Analysis outputs
compile_node = next(n for n in workflow['nodes'] if n['name'] == 'Compile All Chapter Analyses')
compile_node['parameters']['jsCode'] = '''// Collect ALL chapter analyses using $input.all()
const allAnalyses = $input.all();
const config = $('Configuration').first().json;
const manuscript = $('Decode Manuscript').first().json.data;

console.log(`ℹ️  Compiling ${allAnalyses.length} chapter analyses`);

if (allAnalyses.length === 0) {
    console.error('❌ No analyses received!');
    throw new Error('No chapter analyses received. Loop may not have completed.');
}

// Sort by chapter number
const sorted = allAnalyses
    .map(item => item.json)
    .sort((a, b) => a.chapter_number - b.chapter_number);

console.log(`   Chapters: ${sorted.map(a => a.chapter_number).join(', ')}`);

// Build improvement plan
const improvementPlan = {
    diagnostic_summary: {
        total_chapters_analyzed: sorted.length,
        current_word_count: manuscript.split(/\\s+/).length,
        target_word_count: config.target_word_count,
        structural_issues: [],
        prose_issues: config.known_issues
    },
    expansion_plan: {
        chapters_to_expand: [],
        new_chapters: []
    },
    chapter_analyses: []
};

// Process each analysis
sorted.forEach(item => {
    const chapterNum = item.chapter_number;
    const analysis = item.analysis;

    improvementPlan.chapter_analyses.push({
        chapter: chapterNum,
        analysis: analysis || {},
        tokens_used: item.tokens_used || 0
    });

    if (analysis && typeof analysis === 'object') {
        if (analysis.expansion_plan) {
            improvementPlan.expansion_plan.chapters_to_expand.push({
                chapter: chapterNum,
                current_words: item.word_count || 0,
                expansion_method: 'scene_expansion',
                scene_outline: typeof analysis.expansion_plan === 'string'
                    ? analysis.expansion_plan
                    : JSON.stringify(analysis.expansion_plan),
                estimated_words: analysis.estimated_words_to_add || 1000,
                placement: 'throughout_chapter'
            });
        }

        if (analysis.current_issues) {
            const issues = Array.isArray(analysis.current_issues)
                ? analysis.current_issues
                : [`Chapter ${chapterNum}: ${analysis.current_issues}`];
            improvementPlan.diagnostic_summary.structural_issues.push(...issues);
        }
    }
});

const totalTokens = sorted.reduce((sum, item) => sum + (item.tokens_used || 0), 0);

console.log(`\\n✅ Compiled ${sorted.length} chapters`);
console.log(`   Expansions: ${improvementPlan.expansion_plan.chapters_to_expand.length}`);
console.log(`   Tokens: ${totalTokens}`);

return {
    json: {
        improvement_plan: improvementPlan,
        manuscript: manuscript,
        book_id: config.book_id,
        total_tokens: totalTokens,
        chapters_analyzed: sorted.length
    }
};'''

# Save with new timestamp
from datetime import datetime
timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
output_file = f'{timestamp}_workflow-3-ghostwriter-LOOP-FIXED.json'

with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Fixed loop collection pattern:')
print('- Store Chapter Analysis now connects to BOTH Rate Limit AND Compile')
print('- Compile uses $input.all() to collect all Store outputs')
print('- No more accumulation array passing (that pattern does not work in n8n)')
print('- Loop completes, all analyses flow to Compile automatically')
print(f'')
print(f'New file: {output_file}')
