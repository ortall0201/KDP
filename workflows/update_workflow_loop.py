# -*- coding: utf-8 -*-
import json

# Read the current workflow
with open('2026-01-05T23-00-00_workflow-3-ghostwriter-VALIDATED-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find nodes for positioning
decode_node = next(n for n in workflow['nodes'] if n['name'] == 'Decode Manuscript')
config_node = next(n for n in workflow['nodes'] if n['name'] == 'Configuration')

# Remove the old "Build Master Planner Request" node if it exists
workflow['nodes'] = [n for n in workflow['nodes'] if n['name'] != 'Build Master Planner Request']

# 1. Create "Split Manuscript into Chapters" node
split_chapters_node = {
    'parameters': {
        'jsCode': '''// Split manuscript into individual chapters for analysis
const manuscript = $('Decode Manuscript').first().json.data;
const config = $('Configuration').first().json;

// Split by chapter markers
const chapters = manuscript.split(/CHAPTER (?:undefined|\\d+)/gi).filter(c => c.trim().length > 100);

console.log(`ℹ️  Split manuscript into ${chapters.length} chapters`);

// Create items for each chapter
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
            total_chapters: chapters.length
        }
    };
});

return chapterItems;'''
    },
    'id': 'split-chapters-001',
    'name': 'Split Manuscript into Chapters',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_node['position'][0] + 192, decode_node['position'][1]]
}

# 2. Create "PHASE 1: Chapter Analysis Loop" (SplitInBatches)
chapter_loop_node = {
    'parameters': {
        'options': {
            'reset': True
        }
    },
    'id': 'phase1-chapter-loop-001',
    'name': 'PHASE 1: Chapter Analysis Loop',
    'type': 'n8n-nodes-base.splitInBatches',
    'typeVersion': 3,
    'position': [decode_node['position'][0] + 400, decode_node['position'][1]]
}

# 3. Update "Build Master Planner Request" to analyze ONE chapter
build_request_node = {
    'parameters': {
        'jsCode': '''// Build request to analyze ONE chapter
const chapterData = $input.first().json;
const systemPrompt = $('PROMPT: Master Planner').first().json.system_prompt;

// Build focused user prompt for this chapter
const userPrompt = `Analyze CHAPTER ${chapterData.chapter_number} of ${chapterData.total_chapters}:

CHAPTER TEXT (${chapterData.word_count} words):
${chapterData.chapter_text}

KNOWN ISSUES FOR THIS MANUSCRIPT:
${chapterData.known_issues.join('\\n')}

TARGET: Expand from current ${chapterData.word_count} words to ~${Math.round(chapterData.target_word_count / chapterData.total_chapters)} words per chapter.

Analyze this chapter and provide:
1. Current issues (pacing, prose, character development)
2. Expansion opportunities (scenes to add, depth needed)
3. Specific improvements needed

Output in JSON format with keys: chapter, current_issues, expansion_plan, estimated_words_to_add`;

const requestBody = {
    model: 'gpt-4o',
    messages: [
        {
            role: 'system',
            content: systemPrompt
        },
        {
            role: 'user',
            content: userPrompt
        }
    ],
    temperature: 0.7,
    max_tokens: 2000
};

console.log(`ℹ️  Built analysis request for Chapter ${chapterData.chapter_number}`);
console.log(`   Chapter: ${chapterData.word_count} words`);

return {
    json: {
        request_body: requestBody,
        chapter_number: chapterData.chapter_number,
        chapter_text: chapterData.chapter_text,
        word_count: chapterData.word_count
    }
};'''
    },
    'id': 'build-chapter-analysis-request-001',
    'name': 'Build Chapter Analysis Request',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_node['position'][0] + 608, decode_node['position'][1] - 96]
}

# 4. Create "Store Chapter Analysis" node
store_analysis_node = {
    'parameters': {
        'jsCode': '''// Store the analysis for this chapter
const response = $input.item.json;
const chapterNumber = $('PHASE 1: Chapter Analysis Loop').item.json.chapter_number;

// Extract the analysis from response
const analysisText = response.choices[0].message.content;

let chapterAnalysis;
try {
    // Try to parse JSON from response
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

return {
    json: {
        chapter_number: chapterNumber,
        analysis: chapterAnalysis,
        tokens_used: response.usage?.total_tokens || 0
    }
};'''
    },
    'id': 'store-chapter-analysis-001',
    'name': 'Store Chapter Analysis',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_node['position'][0] + 1088, decode_node['position'][1] - 96]
}

# 5. Create "Rate Limit Pause Chapter Analysis" node
rate_limit_node = {
    'parameters': {
        'amount': 5
    },
    'id': 'rate-limit-chapter-analysis-001',
    'name': 'Rate Limit Pause Chapter Analysis',
    'type': 'n8n-nodes-base.wait',
    'typeVersion': 1.1,
    'position': [decode_node['position'][0] + 1264, decode_node['position'][1] - 96],
    'webhookId': 'chapter-analysis-rate-limit-001'
}

# 6. Create "Loop Back Chapter Analysis" node
loop_back_node = {
    'parameters': {},
    'id': 'loop-back-chapter-analysis-001',
    'name': 'Loop Back Chapter Analysis',
    'type': 'n8n-nodes-base.noOp',
    'typeVersion': 1,
    'position': [decode_node['position'][0] + 1440, decode_node['position'][1] - 96]
}

# 7. Create "Compile All Chapter Analyses" node
compile_node = {
    'parameters': {
        'jsCode': '''// Compile all chapter analyses into master improvement plan
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
    chapter_analyses: sorted.map(item => item.json.analysis)
};

// Extract expansion opportunities from each chapter
sorted.forEach(item => {
    const analysis = item.json.analysis;
    if (analysis.expansion_plan) {
        improvementPlan.expansion_plan.chapters_to_expand.push({
            chapter: item.json.chapter_number,
            current_words: 0, // Will be calculated
            expansion_method: 'scene_expansion',
            scene_outline: analysis.expansion_plan,
            estimated_words: analysis.estimated_words_to_add || 1000
        });
    }
});

const totalTokens = sorted.reduce((sum, item) => sum + (item.json.tokens_used || 0), 0);
console.log(`   Total tokens used: ${totalTokens}`);
console.log(`   Chapters to expand: ${improvementPlan.expansion_plan.chapters_to_expand.length}`);

return {
    json: {
        improvement_plan: improvementPlan,
        manuscript: manuscript,
        book_id: config.book_id,
        total_tokens: totalTokens
    }
};'''
    },
    'id': 'compile-chapter-analyses-001',
    'name': 'Compile All Chapter Analyses',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_node['position'][0] + 608, decode_node['position'][1] + 96]
}

# 8. Create "Verify Plan Complete" checkpoint node
verify_node = {
    'parameters': {
        'jsCode': '''// Verify that plan is complete and ready
const plan = $input.item.json.improvement_plan;

const expectedChapters = 15;
const analyzedChapters = plan.chapter_analyses?.length || 0;

if (analyzedChapters < expectedChapters) {
    throw new Error(`Incomplete plan: only ${analyzedChapters} of ${expectedChapters} chapters analyzed`);
}

console.log(`✅ Plan verification passed:`);
console.log(`   Analyzed: ${analyzedChapters} chapters`);
console.log(`   Expansions planned: ${plan.expansion_plan.chapters_to_expand.length}`);

return [$input.item];'''
    },
    'id': 'verify-plan-complete-001',
    'name': 'Verify Plan Complete',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_node['position'][0] + 816, decode_node['position'][1] + 96]
}

# Add all new nodes
workflow['nodes'].extend([
    split_chapters_node,
    chapter_loop_node,
    build_request_node,
    store_analysis_node,
    rate_limit_node,
    loop_back_node,
    compile_node,
    verify_node
])

# Update connections
workflow['connections']['Decode Manuscript'] = {
    'main': [[{'node': 'Split Manuscript into Chapters', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Split Manuscript into Chapters'] = {
    'main': [[{'node': 'PHASE 1: Chapter Analysis Loop', 'type': 'main', 'index': 0}]]
}

workflow['connections']['PHASE 1: Chapter Analysis Loop'] = {
    'main': [
        [{'node': 'Build Chapter Analysis Request', 'type': 'main', 'index': 0}],
        [{'node': 'Compile All Chapter Analyses', 'type': 'main', 'index': 0}]
    ]
}

workflow['connections']['Build Chapter Analysis Request'] = {
    'main': [[{'node': 'PHASE 1: Master Planner', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Validation Gate: Master Planner'] = {
    'main': [[{'node': 'Store Chapter Analysis', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Store Chapter Analysis'] = {
    'main': [[{'node': 'Rate Limit Pause Chapter Analysis', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Rate Limit Pause Chapter Analysis'] = {
    'main': [[{'node': 'Loop Back Chapter Analysis', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Loop Back Chapter Analysis'] = {
    'main': [[{'node': 'PHASE 1: Chapter Analysis Loop', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Compile All Chapter Analyses'] = {
    'main': [[{'node': 'Verify Plan Complete', 'type': 'main', 'index': 0}]]
}

workflow['connections']['Verify Plan Complete'] = {
    'main': [[{'node': 'Parse Plan', 'type': 'main', 'index': 0}]]
}

# Update Parse Plan to not expect the old format
parse_plan_node = next(n for n in workflow['nodes'] if n['name'] == 'Parse Plan')
parse_plan_node['parameters']['jsCode'] = '''// Parse Plan is now already compiled
const plan = $input.item.json;

console.log('ℹ️  Using compiled improvement plan');
console.log('   Chapters analyzed:', plan.improvement_plan.chapter_analyses.length);

return {
    json: {
        improvement_plan: plan.improvement_plan,
        manuscript: plan.manuscript,
        book_id: plan.book_id
    }
};'''

# Save the updated workflow
with open('2026-01-06T00-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Workflow updated with chapter-by-chapter loop architecture')
print('Added nodes:')
print('  - Split Manuscript into Chapters')
print('  - PHASE 1: Chapter Analysis Loop')
print('  - Build Chapter Analysis Request')
print('  - Store Chapter Analysis')
print('  - Rate Limit Pause Chapter Analysis')
print('  - Loop Back Chapter Analysis')
print('  - Compile All Chapter Analyses')
print('  - Verify Plan Complete')
print('Updated connections for loop architecture')
