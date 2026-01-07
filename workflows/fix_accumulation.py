# -*- coding: utf-8 -*-
import json

with open('2026-01-06T01-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Update "Store Chapter Analysis" to accumulate results
store_node = next(n for n in workflow['nodes'] if n['name'] == 'Store Chapter Analysis')

store_node['parameters']['jsCode'] = '''// Store the analysis for this chapter AND accumulate all analyses
const response = $input.first().json;
const loopData = $('PHASE 1: Chapter Analysis Loop').item.json;
const chapterNumber = loopData.chapter_number;

// Extract the analysis from response
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
    // If not JSON, store as text
    chapterAnalysis = {
        chapter: chapterNumber,
        raw_analysis: analysisText
    };
}

console.log(`ℹ️  Stored analysis for Chapter ${chapterNumber}`);

// Get accumulated analyses from previous iterations (if any)
const accumulated = $('PHASE 1: Chapter Analysis Loop').context.accumulated_analyses || [];

// Add current analysis to accumulated list
accumulated.push({
    chapter_number: chapterNumber,
    analysis: chapterAnalysis,
    word_count: loopData.word_count || 0,
    tokens_used: response.usage?.total_tokens || 0
});

// Store back in context for next iteration
$('PHASE 1: Chapter Analysis Loop').context.accumulated_analyses = accumulated;

console.log(`   Total analyses accumulated: ${accumulated.length}/15`);

return {
    json: {
        chapter_number: chapterNumber,
        analysis: chapterAnalysis,
        tokens_used: response.usage?.total_tokens || 0,
        accumulated_count: accumulated.length
    }
};'''

# Update "Compile All Chapter Analyses" to use accumulated data
compile_node = next(n for n in workflow['nodes'] if n['name'] == 'Compile All Chapter Analyses')

compile_node['parameters']['jsCode'] = '''// Compile all chapter analyses from accumulated context
const config = $('Configuration').first().json;
const manuscript = $('Decode Manuscript').first().json.data;

// Get all accumulated analyses from loop context
const accumulated = $('PHASE 1: Chapter Analysis Loop').context.accumulated_analyses || [];

console.log(`ℹ️  Compiling ${accumulated.length} accumulated chapter analyses`);

if (accumulated.length === 0) {
    throw new Error('No chapter analyses were accumulated during the loop');
}

// Sort by chapter number
const sorted = accumulated.sort((a, b) => a.chapter_number - b.chapter_number);

// Build comprehensive improvement plan
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

// Process each chapter analysis
sorted.forEach(item => {
    const chapterNum = item.chapter_number;
    const analysis = item.analysis;

    console.log(`   Processing Chapter ${chapterNum}...`);

    // Store the raw analysis
    improvementPlan.chapter_analyses.push({
        chapter: chapterNum,
        analysis: analysis || {},
        tokens_used: item.tokens_used || 0
    });

    // Try to extract expansion info (defensive)
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
            if (Array.isArray(analysis.current_issues)) {
                improvementPlan.diagnostic_summary.structural_issues.push(
                    ...analysis.current_issues
                );
            } else {
                improvementPlan.diagnostic_summary.structural_issues.push(
                    `Chapter ${chapterNum}: ${analysis.current_issues}`
                );
            }
        }
    }
});

const totalTokens = sorted.reduce((sum, item) => sum + (item.tokens_used || 0), 0);

console.log(`\\n✅ Compilation complete:`);
console.log(`   Chapters analyzed: ${sorted.length}`);
console.log(`   Chapters to expand: ${improvementPlan.expansion_plan.chapters_to_expand.length}`);
console.log(`   Total tokens used: ${totalTokens}`);

return {
    json: {
        improvement_plan: improvementPlan,
        manuscript: manuscript,
        book_id: config.book_id,
        total_tokens: totalTokens,
        chapters_analyzed: sorted.length
    }
};'''

# Save
with open('2026-01-06T02-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Fixed accumulation pattern:')
print('- Store Chapter Analysis now accumulates results in loop context')
print('- Compile All Chapter Analyses reads from accumulated context')
print('- Each iteration adds to the accumulated list')
print('- When loop completes, all 15 analyses are available')
print('')
print('New file: 2026-01-06T02-00-00_workflow-3-ghostwriter-LOOP-FIXED.json')
