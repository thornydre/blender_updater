import desktop_file as df
import os
import platform

exec = ""

if "Windows" in platform.system():
    exec = os.path.join(os.path.dirname(__file__), "../run.bat")
else:
    exec = os.path.join(os.path.dirname(__file__), "../run.sh")

shortcut = df.Shortcut(df.getDesktopPath(), "BlenderUpdater", exec)
shortcut.setTitle("Blender Updater")
shortcut.setWorkingDirectory(os.path.join(os.path.dirname(__file__), "../"))
shortcut.setComment("A GUI for building Blender")
# shortcut.attributes["Terminal"] = "true" # Can you believe python lets you do this smh
shortcut.save()
