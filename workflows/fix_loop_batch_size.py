# -*- coding: utf-8 -*-
import json

# Read the current workflow
with open('2026-01-06T00-30-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'r', encoding='utf-8') as f:
    workflow = json.load(f)

# Find the "PHASE 1: Chapter Analysis Loop" node
loop_node = next(n for n in workflow['nodes'] if n['name'] == 'PHASE 1: Chapter Analysis Loop')

print(f"Current loop configuration:")
print(f"  Parameters: {loop_node['parameters']}")

# Fix: Set batchSize to 1 to process one chapter at a time
loop_node['parameters'] = {
    'batchSize': 1,
    'options': {
        'reset': True
    }
}

print(f"\nUpdated loop configuration:")
print(f"  Parameters: {loop_node['parameters']}")

# Save the updated workflow
with open('2026-01-06T01-00-00_workflow-3-ghostwriter-LOOP-FIXED.json', 'w', encoding='utf-8') as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print('\n✓ Fixed PHASE 1: Chapter Analysis Loop')
print('✓ Set batchSize: 1 (process one chapter at a time)')
print('✓ Loop will now iterate 15 times (once per chapter)')
print('\nNew file: 2026-01-06T01-00-00_workflow-3-ghostwriter-LOOP-FIXED.json')
