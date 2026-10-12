"""Build submission ZIP (no caches/venvs/git/logs/binaries)."""
import os
import zipfile

PKG = 'FINAL_SUBMISSION_PACKAGE'
ZIP = 'FINAL_BTECH_ROAD_ACCIDENT_RESEARCH_SUBMISSION.zip'
SKIP = ('__pycache__', '.git', '.pytest_cache', 'uploads')
n = 0
with zipfile.ZipFile(ZIP, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(PKG):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            p = os.path.join(root, f)
            z.write(p, p)
            n += 1
print('zip files:', n, '| bytes:', os.path.getsize(ZIP))
