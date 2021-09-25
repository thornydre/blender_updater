import platform
from PySide6.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog)
from PySide6.QtCore import Qt
import os


class BlenderUpdaterPreferences(QDialog):
	def __init__(self, parent=None):
		super(BlenderUpdaterPreferences, self).__init__(parent=parent, f=Qt.WindowTitleHint|Qt.WindowSystemMenuHint)

		blender_directory_path = ""
		branches_directory_path = ""
		blender_directory_path, branches_directory_path = self.loadConfig()

		self.setWindowTitle("Blender Updater Preferences")

		main_layout = QVBoxLayout()

		blender_directory_label = QLabel("Path to the Blender dev project :")
		main_layout.addWidget(blender_directory_label)

		blender_directory_layout = QHBoxLayout()
		self.blender_directory_textfield = QLineEdit()
		self.blender_directory_textfield.setText(blender_directory_path)
		blender_directory_layout.addWidget(self.blender_directory_textfield)
		blender_directory_button = QPushButton("Browse")
		blender_directory_button.clicked.connect(self.basePathCommand)
		blender_directory_layout.addWidget(blender_directory_button)
		main_layout.addLayout(blender_directory_layout)

		branches_directory_label = QLabel("Path to building destination :")
		main_layout.addWidget(branches_directory_label)

		branches_directory_layout = QHBoxLayout()
		self.branches_directory_textfield = QLineEdit()
		self.branches_directory_textfield.setText(branches_directory_path)
		branches_directory_layout.addWidget(self.branches_directory_textfield)
		branches_directory_button = QPushButton("Browse")
		branches_directory_button.clicked.connect(self.branchesPathCommand)
		branches_directory_layout.addWidget(branches_directory_button)
		main_layout.addLayout(branches_directory_layout)

		buttons_layout = QHBoxLayout()
		submit_button = QPushButton("Save")
		submit_button.clicked.connect(self.submitCommand)
		buttons_layout.addWidget(submit_button)
		cancel_button = QPushButton("Cancel")
		cancel_button.clicked.connect(self.cancelCommand)
		buttons_layout.addWidget(cancel_button)
		main_layout.addLayout(buttons_layout)

		self.setLayout(main_layout)

		self.resize(600, 100)


	def loadConfig(self):
		if os.path.isfile("./BlenderUpdater.conf"):
			with open("./BlenderUpdater.conf", "r") as f:
				lines = f.readlines()
				try:
					return lines[0].strip("\n"), lines[1]
				except IndexError:
					pass
		else:
			f = open("./BlenderUpdater.conf", "x")
			f.writelines("\n")

		return "", ""


	def basePathCommand(self):
		blender_directory = QFileDialog.getExistingDirectory(caption="Select blender directory", dir=self.blender_directory_textfield.text())

		if blender_directory:
			self.blender_directory_textfield.setText(blender_directory)


	def branchesPathCommand(self):
		branches_directory = QFileDialog.getExistingDirectory(caption="Select branches directory", dir=self.branches_directory_textfield.text())

		if branches_directory:
			self.branches_directory_textfield.setText(branches_directory)


	def cancelCommand(self):
		self.close()


	def submitCommand(self, dict_key):
		blender_directory = self.blender_directory_textfield.text()
		branches_directory = self.branches_directory_textfield.text()
		if blender_directory and branches_directory:
			paths = blender_directory + "\n" + branches_directory
			f = open("./BlenderUpdater.conf", "w")
			f.writelines(paths)
			self.close()
