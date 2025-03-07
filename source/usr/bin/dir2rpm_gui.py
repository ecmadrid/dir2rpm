#!/usr/bin/env python3

import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QFormLayout, QTextEdit)
from PyQt5.QtCore import QCoreApplication, QTranslator, QLocale

class Dir2RPMGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = QTranslator()
        self.load_language()  # Cargar idioma antes de initUI
        self.initUI()

    def load_language(self):
        locale = QLocale.system().name()
        print(f"Detected locale: {locale}")
        qm_path = f"/usr/share/locale/{locale}/LC_MESSAGES/dir2rpm.qm"
        print(f"Looking for: {qm_path}")
        if os.path.exists(qm_path):
            if self.translator.load(qm_path):
                app = QApplication.instance()
                if app is not None:
                    app.installTranslator(self.translator)
                    print(f"Loaded translation: {qm_path}")
                else:
                    print("QApplication instance not found")
            else:
                print(f"Failed to load translation: {qm_path}")
        else:
            print(f"Translation file not found: {qm_path}")

    def initUI(self):
        self.setWindowTitle(QCoreApplication.translate("Dir2RPMGUI", "dir2rpm - Create RPMs Easily"))
        print(f"Title set to: {self.windowTitle()}")
        self.setGeometry(100, 100, 600, 750)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        form_layout = QFormLayout()

        # Directory
        self.dir_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Directory:"))
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton(QCoreApplication.translate("Dir2RPMGUI", "Select"))
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        form_layout.addRow(self.dir_label, dir_layout)

        # Name
        self.name_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Name:"))
        self.name_input = QLineEdit("mypackage")
        form_layout.addRow(self.name_label, self.name_input)

        # Version
        self.version_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Version:"))
        self.version_input = QLineEdit("1.0")
        form_layout.addRow(self.version_label, self.version_input)

        # Release
        self.release_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Release:"))
        self.release_input = QLineEdit("1")
        form_layout.addRow(self.release_label, self.release_input)

        # Summary
        self.summary_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Summary:"))
        self.summary_input = QLineEdit(QCoreApplication.translate("Dir2RPMGUI", "Create an installable binary RPM package from a directory"))
        form_layout.addRow(self.summary_label, self.summary_input)

        # Description
        self.description_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Description:"))
        self.description_input = QTextEdit(QCoreApplication.translate("Dir2RPMGUI", "Create an installable binary RPM package from a directory"))
        form_layout.addRow(self.description_label, self.description_input)

        # License
        self.license_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "License:"))
        self.license_input = QLineEdit("MIT")
        form_layout.addRow(self.license_label, self.license_input)

        # Arch
        self.arch_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Arch:"))
        self.arch_input = QLineEdit("noarch")
        form_layout.addRow(self.arch_label, self.arch_input)

        # Vendor
        self.vendor_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Vendor:"))
        self.vendor_input = QLineEdit("xAI")
        form_layout.addRow(self.vendor_label, self.vendor_input)

        # Depends
        self.depends_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Depends:"))
        self.depends_input = QLineEdit()
        form_layout.addRow(self.depends_label, self.depends_input)

        # Scripts
        self.preinst_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Preinst Script:"))
        self.preinst_input = QTextEdit()
        form_layout.addRow(self.preinst_label, self.preinst_input)

        self.postinst_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Postinst Script:"))
        self.postinst_input = QTextEdit()
        form_layout.addRow(self.postinst_label, self.postinst_input)

        self.preun_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Preun Script:"))
        self.preun_input = QTextEdit()
        form_layout.addRow(self.preun_label, self.preun_input)

        self.postun_label = QLabel(QCoreApplication.translate("Dir2RPMGUI", "Postun Script:"))
        self.postun_input = QTextEdit()
        form_layout.addRow(self.postun_label, self.postun_input)

        layout.addLayout(form_layout)

        self.create_button = QPushButton(QCoreApplication.translate("Dir2RPMGUI", "Create RPM"))
        print(f"Button text: {self.create_button.text()}")
        self.create_button.clicked.connect(self.create_rpm)
        layout.addWidget(self.create_button)

        layout.addStretch()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 
            QCoreApplication.translate("Dir2RPMGUI", "Select Directory"), 
            os.path.expanduser("~"))
        if directory:
            self.dir_input.setText(directory)

    def create_rpm(self):
        directory = self.dir_input.text()
        if not directory or not os.path.isdir(directory):
            QMessageBox.warning(self, 
                QCoreApplication.translate("Dir2RPMGUI", "Error"), 
                QCoreApplication.translate("Dir2RPMGUI", "Please select a directory."))
            return

        # Create metadata.txt
        metadata = (
            f"Name: {self.name_input.text()}\n"
            f"Version: {self.version_input.text()}\n"
            f"Release: {self.release_input.text()}\n"
            f"Summary: {self.summary_input.text()}\n"
            f"Description:\n{self.description_input.toPlainText()}\n"
            f"License: {self.license_input.text()}\n"
            f"Arch: {self.arch_input.text()}\n"
            f"Vendor: {self.vendor_input.text()}\n"
        )
        if self.depends_input.text():
            metadata += f"Depends: {self.depends_input.text()}\n"

        metadata_path = os.path.join(directory, "metadata.txt")
        with open(metadata_path, "w") as f:
            f.write(metadata)

        # Create script files if provided
        scripts = {
            "preinst": self.preinst_input.toPlainText(),
            "postinst": self.postinst_input.toPlainText(),
            "preun": self.preun_input.toPlainText(),
            "postun": self.postun_input.toPlainText()
        }
        for script_name, script_content in scripts.items():
            if script_content.strip():
                script_path = os.path.join(directory, script_name)
                with open(script_path, "w") as f:
                    f.write(script_content)

        try:
            result = subprocess.run(["/usr/bin/dir2rpm.sh", directory], 
                                   capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            rpm_file = output.split()[-1]
            QMessageBox.information(self, 
                QCoreApplication.translate("Dir2RPMGUI", "Success"), 
                QCoreApplication.translate("Dir2RPMGUI", "RPM created: {rpm_file}").format(rpm_file=rpm_file))
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, 
                QCoreApplication.translate("Dir2RPMGUI", "Error"), 
                QCoreApplication.translate("Dir2RPMGUI", "Failed to create RPM:\n{error}").format(error=e.stderr))
        finally:
            # Clean up temporary files
            for file in ["metadata.txt", "preinst", "postinst", "preun", "postun"]:
                file_path = os.path.join(directory, file)
                if os.path.exists(file_path):
                    os.remove(file_path)

def main():
    app = QApplication(sys.argv)
    ex = Dir2RPMGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
