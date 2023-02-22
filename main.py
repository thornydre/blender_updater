from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QComboBox, QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Slot, Qt, QFile, QTextStream
from PySide6.QtGui import QPixmap, QIcon, QAction
from utils.preferences import *
from shutil import rmtree
import threading
import ctypes
import subprocess
import os
import sys
import platform
import json


class BlenderUpdater(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		self.title = "Blender Updater"
		self.preferences = self.loadConfig()

		self.base_path = self.preferences.get("blender_dir")
		self.branches_path = self.preferences.get("branches_dir")
		self.lib_path = self.preferences.get("lib_dir")

		# self.base_path, self.branches_path, self.lib_path = self.loadConfig()
		# self.base_path += "/"

		self.os = platform.system()
		self.initUI()

		self.comboChanged()


	def initUI(self):
		self.setWindowTitle(self.title)

		# if os.path.isdir(self.base_path) and self.base_path != "/":
		# 	git_command = subprocess.run(["git", "-C", self.base_path, "branch", "-a", "--sort=-committerdate"], stdout=subprocess.PIPE)

		# 	raw_data = str(git_command).split("->")[1].split()

		# 	filtered_data = []

		main_widget = QWidget()

		self.open_log_action = QAction("Open build log", self)
		self.open_log_action.triggered.connect(self.openBuildLog)

		self.clean_up_action = QAction("Clean up", self)
		self.clean_up_action.triggered.connect(self.startCleanupThread)

		self.remove_branch_action = QAction("Remove branch", self)
		self.remove_branch_action.triggered.connect(self.removeBranch)

		menu_bar = self.menuBar()

		file_menu = menu_bar.addMenu("File")
		file_menu.addAction(self.open_log_action)
		file_menu.addAction(self.clean_up_action)
		file_menu.addAction(self.remove_branch_action)

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

		if os.path.isdir(self.base_path) and self.base_path != "/":
			for branch_name in self.preferences["branches"]:
				self.branches_combo.addItem(branch_name)

		self.branches_combo.currentTextChanged.connect(self.comboChanged)

		self.diff_textfield = QLineEdit()

		pixmap = QPixmap("./assets/file.png")
		icon = QIcon(pixmap)
		self.diff_browse_button = QPushButton()
		self.diff_browse_button.setFixedWidth(25)
		self.diff_browse_button.setIcon(icon)
		self.diff_browse_button.setIconSize(pixmap.rect().size())
		self.diff_browse_button.clicked.connect(self.browseDiffCommand)

		self.submit_button = QPushButton("Build selected branch")
		self.submit_button.clicked.connect(self.startBuildThread)

		self.progress_label = QLabel("")

		self.abort_button = QPushButton("Abort current build")
		self.abort_button.clicked.connect(self.abortBuild)
		self.abort_button.setEnabled(False)

		self.start_branch_button = QPushButton("Start selected build")
		self.start_branch_button.clicked.connect(self.startBuild)
		self.start_branch_button.setEnabled(False)

		self.title_horizon_layout = QHBoxLayout()
		self.title_horizon_layout.addWidget(title_label)
		self.title_horizon_layout.addWidget(self.parameters_button)

		self.diff_horizon_layout = QHBoxLayout()
		self.diff_horizon_layout.addWidget(self.diff_textfield)
		self.diff_horizon_layout.addWidget(self.diff_browse_button)

		self.vert_layout = QVBoxLayout()
		self.vert_layout.addLayout(self.title_horizon_layout)
		self.vert_layout.addWidget(self.branches_combo)
		self.vert_layout.addLayout(self.diff_horizon_layout)
		self.vert_layout.addWidget(self.submit_button)
		self.vert_layout.addWidget(self.progress_label)
		self.vert_layout.addWidget(self.abort_button)
		self.vert_layout.addWidget(self.start_branch_button)

		main_widget.setLayout(self.vert_layout)

		self.setCentralWidget(main_widget)


	def buildBlender(self, stop_event):
		self.submit_button.setEnabled(False)
		self.start_branch_button.setEnabled(False)
		self.abort_button.setEnabled(True)

		parameters = self.getUpdateScriptParameters(self.branches_combo.currentText())
		with subprocess.Popen(parameters, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=self.getPreexecCallback()) as proc:
			self.child_process = proc

			text = ""
			loop = 0

			while proc.poll() is None:
				output = proc.stdout.readline()
				output_string = output.strip().decode("utf-8")

				if output_string:
					progress = True
					if output_string == "CHECKOUT":
						text = "(1/4) - Checkout"
						self.title = "(1/4) - Blender Updater"
					elif output_string == "UPDATE":
						text = "(2/4) - Update"
						self.title = "(2/4) - Blender Updater"
					elif output_string == "BUILD":
						text = "(3/4) - Build"
						self.title = "(3/4) - Blender Updater"
					elif output_string == "Error during build":
						progress = False
						text = "Error during build"
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


	def cleanupBlender(self, stop_event):
		parameters = self.getCleanupScriptParameters()
		with subprocess.Popen(parameters, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=self.getPreexecCallback()) as proc:
			while proc.poll() is None:
				output = proc.stdout.readline()
				output_string = output.strip().decode("utf-8")

				print(output_string)

		self.cancelThread()


	def getUpdateScriptParameters(self, branch_name):
		if self.os == "Windows":
			return [f"{os.path.dirname(__file__)}/utils/update.bat", branch_name, self.base_path, self.diff_textfield.text()]
		else:
			return ["sh", "./utils/update.sh", branch_name, self.base_path, self.branches_path, self.diff_textfield.text()]


	def getCleanupScriptParameters(self):
		if self.os == "Windows":
			return [f"{os.path.dirname(__file__)}/utils/cleanup.bat", self.lib_path, self.base_path]
		else:
			return None


	def getPreexecCallback(self):
		if self.os == "Windows":
			return None
		else:
			return os.setsid


	def getBranchName(self):
		'''
			Get the branch name to be used in update.sh and linux build paths; assume "master" if nothing is selected
		'''
		selected_branch = self.branches_combo.currentText()
		return selected_branch if selected_branch else "master"


	def getBuildPath(self):
		if self.os == "Windows":
			return f"{self.branches_path}/{self.branches_combo.currentText()}_branch/bin/Release/blender.exe"
		else:
			return os.path.join(self.branches_path, self.getBranchName(), "bin/blender")


	def getBuildLogPath(self):
		if self.os == "Windows":
			return f"{self.branches_path}/{self.branches_combo.currentText()}_branch/Build.log"
		else:
			return ""


	def abortBuild(self):
		if self.child_process:
			self.child_process.terminate()
			self.stop_event.set()
			self.abort_button.setEnabled(False)
			self.start_branch_button.setEnabled(True)
			self.submit_button.setEnabled(True)
			self.progress_label.setText("Aborted")
			self.title = "Blender Updater"
			self.setWindowTitle(self.title)


	def startBuildThread(self):
		if os.path.isfile("./utils/preferences.conf"):
			self.stop_event = threading.Event()
			self.c_thread = threading.Thread(target=self.buildBlender, args=(self.stop_event, ))
			self.c_thread.daemon = True
			self.c_thread.start()
		else:
			self.preferencesCommand()


	def startCleanupThread(self):
		if os.path.isfile("./utils/preferences.conf"):
			self.stop_event = threading.Event()
			self.c_thread = threading.Thread(target=self.cleanupBlender, args=(self.stop_event, ))
			self.c_thread.daemon = True
			self.c_thread.start()
		else:
			self.preferencesCommand()


	def comboChanged(self):
		if self.branches_combo.currentText():
			self.submit_button.setEnabled(True)
		else:
			self.submit_button.setEnabled(False)

		if os.path.exists(self.getBuildPath()):
			self.start_branch_button.setEnabled(True)
		else:
			self.start_branch_button.setEnabled(False)


	def preferencesCommand(self):
		dialog = BlenderUpdaterPreferences(self)
		dialog.exec()


	def startBuild(self):
		path = self.getBuildPath()
		print("START : " + path)
		subprocess.Popen([path])


	def cancelThread(self):
		self.stop_event.set()


	def loadConfig(self):
		if not os.path.isfile("./utils/preferences.conf"):
			self.preferencesCommand()

		preferences = {}

		if os.path.isfile("./utils/preferences.conf"):
			with open("./utils/preferences.conf", "r") as file:
				preferences = json.load(file)
			# with open("./utils/preferences.conf", "r") as f:
			# 	lines = f.readlines()
			# 	try:
			# 		return lines[0].strip("\n"), lines[1].strip("\n"), lines[2].strip("\n")
			# 	except IndexError: # User messed with conf file
			# 		pass
		return preferences


	def openBuildLog(self):
		if os.path.isfile(self.getBuildLogPath()):
			os.startfile(self.getBuildLogPath())


	def removeBranch(self):
		selected_branch = self.branches_combo.currentText()
		if selected_branch:
			branch_path = f"{self.branches_path}/{selected_branch}_branch"
			if os.path.isdir(branch_path):
				print(f"REMOVING : {branch_path}")
				rmtree(branch_path)


	def browseDiffCommand(self):
		diff = QFileDialog.getOpenFileName(caption="Select differencial to apply")

		if diff:
			self.diff_textfield.setText(diff[0])


def main():
	app = QApplication(sys.argv)
	file = QFile("./assets/dark.qss")
	file.open(QFile.ReadOnly | QFile.Text)
	stream = QTextStream(file)
	app.setStyleSheet(stream.readAll())

	widget = BlenderUpdater()
	widget.resize(300, 200)
	widget.show()

	sys.exit(app.exec())

if __name__ == "__main__":
	main()
