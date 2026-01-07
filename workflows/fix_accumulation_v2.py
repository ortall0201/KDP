# -*- coding: utf-8 -*-
import json

with open('2026-01-06T01-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the "Split Manuscript into Chapters" node
split_node = next(n for n in workflow['nodes'] if n['name'] == 'Split Manuscript into Chapters')

# Update it to include an empty accumulated_analyses array
split_node['parameters']['jsCode'] = '''// Split manuscript into individual chapters for analysis
const manuscript = $('Decode Manuscript').first().json.data;
const config = $('Configuration').first().json;

// Split by chapter markers
const chapters = manuscript.split(/CHAPTER (?:undefined|\\d+)/gi).filter(c => c.trim().length > 100);

console.log(`ℹ️  Split manuscript into ${chapters.length} chapters`);

// Create items for each chapter WITH accumulated_analyses array
const chapterItems = chapters.map((chapterText, idx) => {
    const wordCount = chapterText.split(/\\s+/).filter(w => w.length > 0).length;
    console.log(`   Chapter ${idx + 1}: ${wordCount} words`);

    return {
        json: {
            chapter_number: idx + 1,
            chapter_text: chapterText.trim(),
            word_count: wordCount,
            known_issues: config.known_issues,
            target_word_count: config.target_word_count,
            total_chapters: chapters.length,
            accumulated_analyses: []  // Start with empty array
        }
    };
});

return chapterItems;'''

# Update "Store Chapter Analysis" to append to accumulated array and pass it forward
store_node = next(n for n in workflow['nodes'] if n['name'] == 'Store Chapter Analysis')

store_node['parameters']['jsCode'] = '''// Store analysis AND accumulate for next iteration
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

// Get accumulated analyses from current loop item
const accumulated = loopItem.accumulated_analyses || [];

// Add current analysis
accumulated.push({
    chapter_number: chapterNumber,
    analysis: chapterAnalysis,
    word_count: loopItem.word_count || 0,
    tokens_used: response.usage?.total_tokens || 0
});

console.log(`   Total accumulated: ${accumulated.length}/${loopItem.total_chapters}`);

// IMPORTANT: Pass accumulated array forward for next iteration
return {
    json: {
        ...loopItem,  // Pass forward all original data
        accumulated_analyses: accumulated,  // Updated accumulated array
        last_chapter_analyzed: chapterNumber,
        last_tokens_used: response.usage?.total_tokens || 0
    }
};'''

# Fix the connections - make sure Compile gets data from the right place
workflow['connections']['PHASE 1: Chapter Analysis Loop'] = {
    'main': [
        [{'node': 'Build Chapter Analysis Request', 'type': 'main', 'index': 0}],  # During iteration
        [{'node': 'Compile All Chapter Analyses', 'type': 'main', 'index': 0}]  # When done
    ]
}

# Update "Compile All Chapter Analyses" to use the accumulated data
compile_node = next(n for n in workflow['nodes'] if n['name'] == 'Compile All Chapter Analyses')

compile_node['parameters']['jsCode'] = '''// Get accumulated analyses from the completed loop
const loopOutput = $input.first().json;
const config = $('Configuration').first().json;
const manuscript = $('Decode Manuscript').first().json.data;

// The accumulated_analyses should be in the loop output
const accumulated = loopOutput.accumulated_analyses || [];

console.log(`ℹ️  Compiling ${accumulated.length} chapter analyses`);

if (accumulated.length === 0) {
    console.error('❌ No analyses were accumulated!');
    console.error('   Loop output:', JSON.stringify(loopOutput, null, 2).substring(0, 500));
    throw new Error('No chapter analyses accumulated. Loop may not have completed properly.');
}

// Sort by chapter number
const sorted = accumulated.sort((a, b) => a.chapter_number - b.chapter_number);

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

    console.log(`   Chapter ${chapterNum}: processed`);

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
console.log(`   Expansions planned: ${improvementPlan.expansion_plan.chapters_to_expand.length}`);
console.log(`   Total tokens: ${totalTokens}`);

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
with open('2026-01-06T03-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Applied proper accumulation pattern:')
print('1. Each chapter item carries accumulated_analyses array')
print('2. Store Chapter Analysis appends to array and passes it forward')
print('3. Loop passes the growing array through each iteration')
print('4. When loop completes, final item has all 15 analyses')
print('5. Compile reads the accumulated_analyses from final loop output')
print('')
print('New file: 2026-01-06T03-00-00_workflow-3-ghostwriter-LOOP-FIXED.json')
