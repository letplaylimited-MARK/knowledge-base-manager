import shutil
from pathlib import Path

ROOT_DATA = Path('memory_data')
TARGET = Path('.workbuddy/记忆层/memory_data')

print(f'Root memory_data:  exists={ROOT_DATA.exists()}')
print(f'Target memory_data: exists={TARGET.exists()}')

if ROOT_DATA.exists():
    # Backup: list old files
    old_files = list(ROOT_DATA.rglob('*'))
    print(f'Old files to migrate: {len(old_files)}')
    for f in old_files:
        print(f'  {f.relative_to(ROOT_DATA)}')

    # Create target
    TARGET.mkdir(parents=True, exist_ok=True)

    # Copy all content
    for f in old_files:
        if f.is_dir():
            continue
        rel = f.relative_to(ROOT_DATA)
        dest = TARGET / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        print(f'  Copied: {rel}')

    # Remove old
    shutil.rmtree(ROOT_DATA)
    print('Removed old root memory_data/')
else:
    TARGET.mkdir(parents=True, exist_ok=True)
    print('Target created (no old data to migrate)')

# Verify
print('\nFinal target:')
if TARGET.exists():
    for f in TARGET.rglob('*'):
        if f.is_file():
            print(f'  {f.relative_to(TARGET)} ({f.stat().st_size} bytes)')
