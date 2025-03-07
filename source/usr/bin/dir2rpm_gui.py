#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, 
                             QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt, QTranslator, QLocale

class Dir2RPMGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("dir2rpm - Create RPMs Easily"))
        self.setGeometry(100, 100, 600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(self.tr("Directory:"))
        self.dir_entry = QLineEdit()
        self.dir_button = QPushButton(self.tr("Select"))
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_entry)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)

        metadata_layout = QFormLayout()
        self.metadata_fields = {
            "Name": QLineEdit("mypackage"),
            "Version": QLineEdit("1.0"),
            "Release": QLineEdit("1"),
            "Summary": QLineEdit(self.tr("Binary package generated from directory")),
            "License": QLineEdit("MIT"),
            "Arch": QLineEdit("noarch"),
            "Description": QTextEdit(self.tr("Binary package generated from directory")),
            "Depends": QLineEdit("")
        }
        for field, widget in self.metadata_fields.items():
            metadata_layout.addRow(f"{field}:", widget)
        layout.addLayout(metadata_layout)

        scripts_layout = QFormLayout()
        self.script_fields = {
            "preinst": QLineEdit(),
            "postinst": QLineEdit(),
            "preun": QLineEdit(),
            "postun": QLineEdit()
        }
        for script, entry in self.script_fields.items():
            button = QPushButton(self.tr("Load"))
            button.clicked.connect(lambda _, s=script: self.load_script(s))
            hbox = QHBoxLayout()
            hbox.addWidget(entry)
            hbox.addWidget(button)
            scripts_layout.addRow(f"{script}:", hbox)
        layout.addLayout(scripts_layout)

        self.create_button = QPushButton(self.tr("Create RPM"))
        self.create_button.clicked.connect(self.create_rpm)
        self.create_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(self.create_button, alignment=Qt.AlignCenter)

        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QLineEdit, QTextEdit { padding: 5px; }
            QPushButton { padding: 5px; }
        """)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, self.tr("Select Directory"))
        if directory:
            self.dir_entry.setText(directory)

    def load_script(self, script_name):
        script_path = QFileDialog.getOpenFileName(self, self.tr("Load {script_name}").format(script_name=script_name), "", "Shell scripts (*.sh);;All files (*)")[0]
        if script_path:
            self.script_fields[script_name].setText(script_path)

    def create_rpm(self):
        temp_dir = "temp_dir2rpm"
        os.makedirs(temp_dir, exist_ok=True)

        dir_path = self.dir_entry.text()
        if not dir_path:
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please select a directory."))
            return
        shutil.copytree(dir_path, temp_dir, dirs_exist_ok=True)

        metadata_content = ""
        for field, widget in self.metadata_fields.items():
            value = widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text()
            if value and value != self.metadata_fields[field].placeholderText():
                metadata_content += f"{field}: {value}\n"
        if metadata_content:
            with open(f"{temp_dir}/metadata.txt", "w") as f:
                f.write(metadata_content)

        for script, entry in self.script_fields.items():
            script_path = entry.text()
            if script_path and os.path.exists(script_path):
                shutil.copy(script_path, f"{temp_dir}/{script}")

        try:
            result = subprocess.run(["/usr/bin/dir2rpm.sh", temp_dir], capture_output=True, text=True, check=True)
            rpm_file = result.stdout.strip().split("RPM created: ")[-1]
            if os.path.exists(rpm_file):
                QMessageBox.information(self, self.tr("Success"), self.tr("RPM created: {rpm_file}").format(rpm_file=rpm_file))
            else:
                QMessageBox.critical(self, self.tr("Error"), self.tr("RPM file '{rpm_file}' not found.").format(rpm_file=rpm_file))
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to create RPM:\n{error}").format(error=e.stderr))
        finally:
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = QTranslator()
    locale = QLocale.system().name()  # e.g., "en_US" or "es_ES"
    if translator.load(f"dir2rpm_{locale}", "locale"):
        app.installTranslator(translator)
    window = Dir2RPMGUI()
    window.show()
    sys.exit(app.exec_())
