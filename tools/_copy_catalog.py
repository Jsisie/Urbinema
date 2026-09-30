import shutil
from pathlib import Path

root = Path(r"D:\Programs\Android_Studio\projets\Urbinema")
src = root / "app/src/main/assets/catalog/catalog_v3.json"
dst = root / "app/src/main/assets/catalog/catalog.json"
tmp = dst.with_suffix(".json.tmp")
shutil.copyfile(src, tmp)
tmp.replace(dst)
print("copied", dst.stat().st_size)
