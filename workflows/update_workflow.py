# -*- coding: utf-8 -*-
import json

# Read the current workflow
with open('2026-01-05T22-30-00_workflow-3-ghostwriter-VALIDATED-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the 'Decode Manuscript' node to get its position
decode_node = next(n for n in workflow['nodes'] if n['name'] == 'Decode Manuscript')
decode_pos = decode_node['position']

# Create JavaScript code for the new node
js_code = """// Build OpenAI API Request for Master Planner
const manuscript = $('Decode Manuscript').first().json.data;
const systemPrompt = $('PROMPT: Master Planner').first().json.system_prompt;
const config = $('Configuration').first().json;

// Build the user prompt
const userPrompt = `MANUSCRIPT:

${manuscript}

KNOWN ISSUES:
${config.known_issues.join('\\n')}

Current word count: ${manuscript.split(/\\s+/).length}
Target word count: ${config.target_word_count}

Generate the improvement plan in JSON format.`;

// Build the complete request body
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
    max_tokens: 4000
};

console.log('\\u2139\\ufe0f  Built Master Planner request');
console.log(`   Manuscript: ${manuscript.split(/\\s+/).length} words`);
console.log(`   System prompt: ${systemPrompt.length} chars`);

return {
    json: {
        request_body: requestBody,
        ...config
    }
};"""

# Create a new Code node to build the Master Planner request
build_request_node = {
    'parameters': {
        'jsCode': js_code
    },
    'id': 'build-master-planner-request-001',
    'name': 'Build Master Planner Request',
    'type': 'n8n-nodes-base.code',
    'typeVersion': 2,
    'position': [decode_pos[0] + 192, decode_pos[1] + 100]
}

# Add the new node
workflow['nodes'].append(build_request_node)

# Update the PHASE 1: Master Planner node to use simple jsonBody
master_planner_node = next(n for n in workflow['nodes'] if n['name'] == 'PHASE 1: Master Planner')
master_planner_node['parameters']['jsonBody'] = '={{ $json.request_body }}'

# Update connections
# Decode Manuscript should connect to Build Master Planner Request
workflow['connections']['Decode Manuscript'] = {
    'main': [[{'node': 'Build Master Planner Request', 'type': 'main', 'index': 0}]]
}

# Build Master Planner Request should connect to PHASE 1: Master Planner
workflow['connections']['Build Master Planner Request'] = {
    'main': [[{'node': 'PHASE 1: Master Planner', 'type': 'main', 'index': 0}]]
}

# Save the updated workflow
with open('2026-01-05T23-00-00_workflow-3-ghostwriter-VALIDATED-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('Workflow updated successfully')
print('Added: Build Master Planner Request node')
print('Updated: PHASE 1: Master Planner node')
print('Updated: Workflow connections')
