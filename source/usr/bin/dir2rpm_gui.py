#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, 
                             QMessageBox, QFormLayout)
from PyQt5.QtCore import Qt

class Dir2RPMGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("dir2rpm - Crear RPMs fácilmente")
        self.setGeometry(100, 100, 600, 500)

        # Widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Sección de directorio
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel("Directorio:")
        self.dir_entry = QLineEdit()
        self.dir_button = QPushButton("Seleccionar")
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_entry)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)

        # Sección de metadatos
        metadata_layout = QFormLayout()
        self.metadata_fields = {
            "Name": QLineEdit("mypackage"),
            "Version": QLineEdit("1.0"),
            "Release": QLineEdit("1"),
            "Summary": QLineEdit("Paquete binario generado desde directorio"),
            "License": QLineEdit("MIT"),
            "Arch": QLineEdit("noarch"),
            "Description": QTextEdit("Paquete binario generado desde directorio"),
            "Depends": QLineEdit("")
        }
        for field, widget in self.metadata_fields.items():
            metadata_layout.addRow(f"{field}:", widget)
        layout.addLayout(metadata_layout)

        # Sección de scripts
        scripts_layout = QFormLayout()
        self.script_fields = {
            "preinst": QLineEdit(),
            "postinst": QLineEdit(),
            "preun": QLineEdit(),
            "postun": QLineEdit()
        }
        for script, entry in self.script_fields.items():
            button = QPushButton("Cargar")
            button.clicked.connect(lambda _, s=script: self.load_script(s))
            hbox = QHBoxLayout()
            hbox.addWidget(entry)
            hbox.addWidget(button)
            scripts_layout.addRow(f"{script}:", hbox)
        layout.addLayout(scripts_layout)

        # Botón Crear RPM
        self.create_button = QPushButton("Crear RPM")
        self.create_button.clicked.connect(self.create_rpm)
        self.create_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        layout.addWidget(self.create_button, alignment=Qt.AlignCenter)

        # Estilo general
        self.setStyleSheet("""
            QWidget { font-size: 14px; }
            QLineEdit, QTextEdit { padding: 5px; }
            QPushButton { padding: 5px; }
        """)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if directory:
            self.dir_entry.setText(directory)

    def load_script(self, script_name):
        script_path = QFileDialog.getOpenFileName(self, f"Cargar {script_name}", "", "Shell scripts (*.sh);;All files (*)")[0]
        if script_path:
            self.script_fields[script_name].setText(script_path)

    def create_rpm(self):
        temp_dir = "temp_dir2rpm"
        os.makedirs(temp_dir, exist_ok=True)

        # Copiar archivos del directorio seleccionado
        dir_path = self.dir_entry.text()
        if not dir_path:
            QMessageBox.warning(self, "Error", "Por favor, selecciona un directorio.")
            return
        shutil.copytree(dir_path, temp_dir, dirs_exist_ok=True)

        # Escribir metadata.txt
        metadata_content = ""
        for field, widget in self.metadata_fields.items():
            value = widget.toPlainText() if isinstance(widget, QTextEdit) else widget.text()
            if value and value != self.metadata_fields[field].placeholderText():
                metadata_content += f"{field}: {value}\n"
        if metadata_content:
            with open(f"{temp_dir}/metadata.txt", "w") as f:
                f.write(metadata_content)

        # Copiar scripts
        for script, entry in self.script_fields.items():
            script_path = entry.text()
            if script_path and os.path.exists(script_path):
                shutil.copy(script_path, f"{temp_dir}/{script}")

        # Ejecutar dir2rpm.sh desde /usr/bin
        try:
            result = subprocess.run(["/usr/bin/dir2rpm.sh", temp_dir], capture_output=True, text=True, check=True)
            rpm_file = result.stdout.strip().split("RPM creado: ")[-1]
            # Verificar que el archivo existe, no moverlo porque ya está en el directorio actual
            if os.path.exists(rpm_file):
                QMessageBox.information(self, "Éxito", f"RPM creado: {rpm_file}")
            else:
                QMessageBox.critical(self, "Error", f"El archivo RPM '{rpm_file}' no se encontró.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Fallo al crear el RPM:\n{e.stderr}")
        finally:
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dir2RPMGUI()
    window.show()
    sys.exit(app.exec_())
