from PySide6.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QListWidget)
from PySide6.QtCore import Qt
import os
import json
import subprocess


class BlenderUpdaterPreferences(QDialog):
	def __init__(self, parent=None):
		super(BlenderUpdaterPreferences, self).__init__(parent=parent, f=Qt.WindowTitleHint|Qt.WindowSystemMenuHint)

		preferences = self.loadConfig()

		# blender_directory_path = ""
		# branches_directory_path = ""
		# lib_directory_path = ""
		blender_directory_path = preferences.get("blender_dir")
		branches_directory_path = preferences.get("branches_dir")
		lib_directory_path = preferences.get("lib_dir")
		selected_branches = preferences.get("branches")

		# blender_directory_path, branches_directory_path, lib_directory_path = self.loadConfig()

		self.setWindowTitle("Blender Updater Preferences")

		main_layout = QVBoxLayout()

		blender_directory_label = QLabel("Path to the Blender dev project :")
		main_layout.addWidget(blender_directory_label)

		blender_directory_layout = QHBoxLayout()
		self.blender_directory_textfield = QLineEdit()
		self.blender_directory_textfield.setText(blender_directory_path)
		self.blender_directory_textfield.textChanged.connect(self.updateBlenderDirCommand)
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

		lib_directory_label = QLabel("Path to libraries (clean up) :")
		main_layout.addWidget(lib_directory_label)

		lib_directory_layout = QHBoxLayout()
		self.lib_directory_textfield = QLineEdit()
		self.lib_directory_textfield.setText(lib_directory_path)
		lib_directory_layout.addWidget(self.lib_directory_textfield)
		lib_directory_button = QPushButton("Browse")
		lib_directory_button.clicked.connect(self.libPathCommand)
		lib_directory_layout.addWidget(lib_directory_button)
		main_layout.addLayout(lib_directory_layout)

		branches_list_layout = QHBoxLayout()
		self.all_branches_list = QListWidget()
		self.updateBranchesList()
		branches_list_layout.addWidget(self.all_branches_list)
		self.add_to_selected_list_button = QPushButton(">")
		self.add_to_selected_list_button.clicked.connect(self.addToSelectedListCommand)
		branches_list_layout.addWidget(self.add_to_selected_list_button)
		self.remove_from_selected_list_button = QPushButton("<")
		self.remove_from_selected_list_button.clicked.connect(self.removeFromSelectedListCommand)
		branches_list_layout.addWidget(self.remove_from_selected_list_button)
		self.selected_branches_list = QListWidget()
		for branch_name in selected_branches:
			self.selected_branches_list.addItem(branch_name)
		branches_list_layout.addWidget(self.selected_branches_list)
		main_layout.addLayout(branches_list_layout)

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
		preferences = {}
		if os.path.isfile("./utils/preferences.conf"):
			with open("./utils/preferences.conf", "r") as file:
				preferences = json.load(file)
			# with open("./utils/preferences.conf", "r") as f:
			# 	lines = f.readlines()
			# 	try:
			# 		return lines[0].strip("\n"), lines[1].strip("\n"), lines[2].strip("\n")
			# 	except IndexError:
			# 		pass

		return preferences


	def basePathCommand(self):
		blender_directory = QFileDialog.getExistingDirectory(caption="Select blender directory", dir=self.blender_directory_textfield.text())

		if blender_directory:
			self.blender_directory_textfield.setText(blender_directory)


	def branchesPathCommand(self):
		branches_directory = QFileDialog.getExistingDirectory(caption="Select branches directory", dir=self.branches_directory_textfield.text())

		if branches_directory:
			self.branches_directory_textfield.setText(branches_directory)


	def libPathCommand(self):
		lib_directory = QFileDialog.getExistingDirectory(caption="Select libraries directory", dir=self.lib_directory_textfield.text())

		if lib_directory:
			self.lib_directory_textfield.setText(lib_directory)


	def addToSelectedListCommand(self):
		item = self.all_branches_list.currentItem()
		row = self.all_branches_list.row(item)
		self.all_branches_list.takeItem(row)

		self.selected_branches_list.addItem(item)


	def removeFromSelectedListCommand(self):
		item = self.selected_branches_list.currentItem()
		row = self.selected_branches_list.row(item)
		self.selected_branches_list.takeItem(row)

		self.all_branches_list.addItem(item)


	def updateBlenderDirCommand(self):
		blender_directory = self.blender_directory_textfield.text()

		git_command = subprocess.call(["git", "-C", blender_directory, "branch"], stderr=subprocess.STDOUT, stdout=open(os.devnull, "w"))

		if git_command == 0:
			self.updateBranchesList()


	def updateBranchesList(self):
			blender_directory = self.blender_directory_textfield.text()

			git_command = subprocess.run(["git", "-C", blender_directory, "branch", "-a"], stdout=subprocess.PIPE)

			raw_data = str(git_command).split("->")[1].split()

			filtered_data = []

			self.all_branches_list.clear()

			for data in raw_data:
				branch_name = data.split("/")[-1].split("\\n")[0]
				if branch_name not in filtered_data:
					filtered_data.append(branch_name)
					self.all_branches_list.addItem(branch_name)


	def cancelCommand(self):
		self.close()


	def submitCommand(self, dict_key):
		blender_directory = self.blender_directory_textfield.text()
		branches_directory = self.branches_directory_textfield.text()
		lib_directory = self.lib_directory_textfield.text()

		if blender_directory and branches_directory and lib_directory:
			paths = blender_directory + "\n" + branches_directory + "\n" + lib_directory

			pref_dict = {
				"blender_dir": blender_directory,
				"branches_dir": branches_directory,
				"lib_dir": lib_directory,
				"branches": [self.selected_branches_list.item(index).text() for index in range(self.selected_branches_list.count())]
			}
			with open("./utils/preferences.conf", "w") as file:
				json.dump(pref_dict, file)

			# f = open("./utils/preferences.conf", "w")
			# f.writelines(paths)
			self.close()
