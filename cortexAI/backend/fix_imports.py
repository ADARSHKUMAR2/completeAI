import os
import re

def fix_imports(base_dir, service_name):
    # Matches "from config..." or "from controllers..." etc.
    pattern = re.compile(r'^from (config|controllers|routes|models|utils|graph|agents)(\.| )', re.MULTILINE)
    
    count = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = pattern.sub(rf'from services.{service_name}.\1\2', content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Updated: {filepath}")
                    count += 1
    print(f"Total files updated in {service_name}: {count}")

if __name__ == "__main__":
    fix_imports('services/agent', 'agent')
    fix_imports('services/billing', 'billing')