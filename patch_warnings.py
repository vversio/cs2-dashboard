import os

directories = [r"d:\projects\cs2-dashboard", r"d:\projects\cs2-dashboard\pages"]

for d in directories:
    for filename in os.listdir(d):
        if filename.endswith(".py"):
            filepath = os.path.join(d, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content.replace("width="stretch"", 'width="stretch"')
            new_content = new_content.replace("width="content"", 'width="content"')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
print("use_container_width warnings patched.")
