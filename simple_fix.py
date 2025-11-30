"""Fix dashboard - replace match_found with match and status."""

# Read the original working dashboard backup
with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Simple find and replace for the key issue
content = content.replace("result['match_found']", "result.get('match', result.get('match_found', False))")
content = content.replace("result.get('message', 'This cow is not registered in the database.')", "result.get('message', 'Unknown')")

# Write the fixed version
with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ Dashboard fixed with backward compatibility!")
