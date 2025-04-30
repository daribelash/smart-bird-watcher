import os
import re

def rename_image_name(folder_path: str) -> None:
  folder_name = os.path.basename(os.path.normpath(folder_path))

  files_list = [f for f in os.listdir(folder_path)
    if os.path.isfile(os.path.join(folder_path, f)) and not (f.startswith('.') or f == "DS_Store")]

  files_list.sort(key=lambda f: int(re.sub('\D', '', f)))

  for idx, old_fname in enumerate(files_list, start=1):
    _, extension = os.path.splitext(old_fname)
    new_fname = f"{folder_name}_{idx}{extension.lower()}"
    old_fpath = os.path.join(folder_path, old_fname)
    new_fpath = os.path.join(folder_path, new_fname)
    if old_fname != new_fname:
      os.rename(old_fpath, new_fpath)
  print(f'Finished renaming {folder_name} with {len(files_list)} files.\n')