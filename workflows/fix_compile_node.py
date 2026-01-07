# -*- coding: utf-8 -*-
import json

# Read the current workflow
with open('2026-01-06T00-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find and update the "Compile All Chapter Analyses" node
compile_node = next(n for n in workflow['nodes'] if n['name'] == 'Compile All Chapter Analyses')

# Updated code with better error handling
compile_node['parameters']['jsCode'] = '''// Compile all chapter analyses into master improvement plan
const allAnalyses = $input.all();
const config = $('Configuration').first().json;
const manuscript = $('Decode Manuscript').first().json.data;

console.log(`ℹ️  Compiling ${allAnalyses.length} chapter analyses`);

// Sort by chapter number
const sorted = allAnalyses.sort((a, b) => a.json.chapter_number - b.json.chapter_number);

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

// Process each chapter analysis with defensive checks
sorted.forEach(item => {
    const chapterNum = item.json.chapter_number;
    const analysis = item.json.analysis;

    console.log(`   Processing Chapter ${chapterNum}...`);

    // Store the raw analysis
    improvementPlan.chapter_analyses.push({
        chapter: chapterNum,
        analysis: analysis || {},
        tokens_used: item.json.tokens_used || 0
    });

    // Try to extract expansion info (defensive)
    if (analysis && typeof analysis === 'object') {
        // Check for expansion_plan property
        if (analysis.expansion_plan) {
            improvementPlan.expansion_plan.chapters_to_expand.push({
                chapter: chapterNum,
                current_words: item.json.word_count || 0,
                expansion_method: 'scene_expansion',
                scene_outline: typeof analysis.expansion_plan === 'string'
                    ? analysis.expansion_plan
                    : JSON.stringify(analysis.expansion_plan),
                estimated_words: analysis.estimated_words_to_add || 1000,
                placement: 'throughout_chapter'
            });
        }

        // Check for current_issues
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
    } else {
        console.log(`   ⚠️  Chapter ${chapterNum}: Invalid analysis format`);
    }
});

const totalTokens = sorted.reduce((sum, item) => sum + (item.json.tokens_used || 0), 0);

console.log(`\\n✅ Compilation complete:`);
console.log(`   Chapters analyzed: ${sorted.length}`);
console.log(`   Chapters to expand: ${improvementPlan.expansion_plan.chapters_to_expand.length}`);
console.log(`   Total tokens used: ${totalTokens}`);
console.log(`   Structural issues identified: ${improvementPlan.diagnostic_summary.structural_issues.length}`);

return {
    json: {
        improvement_plan: improvementPlan,
        manuscript: manuscript,
        book_id: config.book_id,
        total_tokens: totalTokens,
        chapters_analyzed: sorted.length
    }
};'''

# Save the updated workflow
with open('2026-01-06T00-30-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Updated Compile All Chapter Analyses node with better error handling')
print('- Added defensive null checks')
print('- Added typeof checks before accessing properties')
print('- Added logging for debugging')
print('- Handles missing or malformed analysis data gracefully')
print('\\nNew file: 2026-01-06T00-30-00_workflow-3-ghostwriter-LOOP-FIXED.json')
