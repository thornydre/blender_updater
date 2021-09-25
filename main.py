import threading
import ctypes
import subprocess
import os
import sys
import platform
from PySide6.QtWidgets import (QApplication, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget)
from PySide6.QtCore import Slot, Qt, QFile, QTextStream
from PySide6.QtGui import QPixmap, QIcon
from utils.preferences import *

class BlenderUpdater(QWidget):
	def __init__(self):
		QWidget.__init__(self)

		self.title = "Blender Updater"
		self.base_path, self.branches_path = self.loadConfig()
		self.base_path += "/"

		self.os = platform.system()

		self.initUI()

		self.comboChanged()


	def initUI(self):
		self.setWindowTitle(self.title)

		git_command = subprocess.run(["git", "-C", self.base_path, "branch", "-a", "--sort=-committerdate"], stdout=subprocess.PIPE)

		raw_data = str(git_command).split("->")[1].split()

		filtered_data = []

		title_label = QLabel("Blender Updater")
		title_label.setAlignment(Qt.AlignCenter)

		pixmap = QPixmap("./assets/gear.png")
		icon = QIcon(pixmap)
		self.parameters_button = QPushButton()
		self.parameters_button.setFixedWidth(25)
		self.parameters_button.setIcon(icon)
		self.parameters_button.setIconSize(pixmap.rect().size())
		self.parameters_button.clicked.connect(self.preferencesCommand)

		self.branches_combo = QComboBox(self)

		for data in raw_data:
			branch_name = data.split("/")[-1].split("\\n")[0]
			if branch_name not in filtered_data:
				filtered_data.append(branch_name)
				self.branches_combo.addItem(branch_name)

		self.branches_combo.currentTextChanged.connect(self.comboChanged)

		self.submit_button = QPushButton("Build selected branch")
		self.submit_button.clicked.connect(self.startThread)

		self.progress_label = QLabel("")

		self.abort_button = QPushButton("Abort current build")
		self.abort_button.clicked.connect(self.abortBuild)
		self.abort_button.setEnabled(False)

		self.start_branch_button = QPushButton("Start selected build")
		self.start_branch_button.clicked.connect(self.startBuild)
		self.start_branch_button.setEnabled(False)

		self.horizon_layout = QHBoxLayout()
		self.horizon_layout.addWidget(title_label)
		self.horizon_layout.addWidget(self.parameters_button)
		
		self.vert_layout = QVBoxLayout()
		self.vert_layout.addLayout(self.horizon_layout)
		self.vert_layout.addWidget(self.branches_combo)
		self.vert_layout.addWidget(self.submit_button)
		self.vert_layout.addWidget(self.progress_label)
		self.vert_layout.addWidget(self.abort_button)
		self.vert_layout.addWidget(self.start_branch_button)
		self.setLayout(self.vert_layout)


	def buildBlender(self, stop_event):
		self.submit_button.setEnabled(False)
		self.start_branch_button.setEnabled(False)
		self.abort_button.setEnabled(True)

		parameters = [os.path.dirname(__file__) + "/utils/update.bat", self.branches_combo.currentText()]
		parameters.append(self.base_path)

		with subprocess.Popen(parameters, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as proc:
			self.batch_process = proc

			text = ""
			loop = 0

			while proc.poll() is None:
				output = proc.stdout.readline()
				output_string = output.strip().decode("utf-8")
				
				if output_string:
					progress = True
					if output_string == "CHECKOUT":
						text = "(1/4) - Checkout"
						# self.progress_label.setText("(1/4) - Checkout")
						self.title = "(1/4) - Blender Updater"
					elif output_string == "UPDATE":
						text = "(2/4) - Update"
						# self.progress_label.setText("(2/4) - Update")
						self.title = "(2/4) - Blender Updater"
					elif output_string == "BUILD":
						text = "(3/4) - Build"
						# self.progress_label.setText("(3/4) - Build")
						self.title = "(3/4) - Blender Updater"
					elif output_string == "Error during build":
						progress = False
						text = "Error during build"
						# self.progress_label.setText("Error during build")
						self.title = "Blender Updater"

				if progress:
					dots = int(loop % 4)
					dots_text = ""
					for i in range(dots):
						dots_text += "."

				self.progress_label.setText(text + dots_text)

				self.setWindowTitle(self.title)
				
				print(output_string)

				loop += 1

		self.progress_label.setText("(4/4) - Done")
		self.title = "Blender Updater"
		self.abort_button.setEnabled(False)
		self.start_branch_button.setEnabled(True)
		self.submit_button.setEnabled(True)
			
		self.setWindowTitle(self.title)

		if self.os == "Windows":
			for i in range(5):
				ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)

		self.cancelThread()


	def abortBuild(self):
		if self.batch_process:
			self.batch_process.terminate()
			self.stop_event.set()
			self.abort_button.setEnabled(False)
			self.start_branch_button.setEnabled(True)
			self.submit_button.setEnabled(True)
			self.progress_label.setText("Aborted")
			self.title = "Blender Updater"
			self.setWindowTitle(self.title)


	def startThread(self):
		if os.path.isfile("./utils/preferences.conf"):
			self.stop_event = threading.Event()
			self.c_thread = threading.Thread(target=self.buildBlender, args=(self.stop_event, ))
			self.c_thread.start()
		else:
			self.preferencesCommand()


	def comboChanged(self):
		path = self.branches_path + "/" + self.branches_combo.currentText() + "_branch/bin/Release/blender.exe"

		if os.path.exists(path):
			self.start_branch_button.setEnabled(True)
		else:
			self.start_branch_button.setEnabled(False)


	def preferencesCommand(self):
		dialog = BlenderUpdaterPreferences(self)
		dialog.exec_()


	def startBuild(self):
		path = self.branches_path + "/" + self.branches_combo.currentText() + "_branch/bin/Release/blender.exe"
		print("START : " + path)
		subprocess.Popen([path])


	def cancelThread(self):
		self.stop_event.set()


	def loadConfig(self):
		if not os.path.isfile("./utils/preferences.conf"):
			self.preferencesCommand()

		with open("./utils/preferences.conf", "r") as f:
			lines = f.readlines()
			
			return lines[0].strip("\n"), lines[1]
		
		return "", ""


def main():
	app = QApplication(sys.argv)
	file = QFile("./assets/dark.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())

	widget = BlenderUpdater()
	widget.resize(300, 200)
	widget.show()

	sys.exit(app.exec_())

if __name__ == "__main__":
	main()