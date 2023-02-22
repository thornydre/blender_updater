import subprocess
import os

base_path = "C:/Users/l.boutrot/Documents/GitHub/blender_updater"

git_command = subprocess.call(["git", "-C", base_path, "branch"], stderr=subprocess.STDOUT, stdout=open(os.devnull, 'w'))

print(git_command)