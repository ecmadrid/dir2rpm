import sys  # Necesario para sys.argv y sys.exit
import os
import subprocess
import glob
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTextEdit, QFileDialog, QComboBox, QTabWidget, 
                            QDialog, QDialogButtonBox, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor

class SpecPreviewDialog(QDialog):
    def __init__(self, spec_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Vista Previa del Archivo SPEC")
        self.setGeometry(100, 100, 600, 400)
        self.setMinimumSize(400, 300)
        
        # Aplicar tema claro al diálogo
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, Qt.black)
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        self.spec_text = QTextEdit()
        self.spec_text.setReadOnly(False)
        self.spec_text.setText(spec_content)
        layout.addWidget(self.spec_text)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Save).clicked.connect(self.save_spec)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.spec_file_path = None
    
    def save_spec(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Guardar Archivo SPEC", "", "SPEC Files (*.spec);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as f:
                f.write(self.spec_text.toPlainText())
            self.spec_file_path = file_name
            self.accept()

class Dir2RPMWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dir2RPM GUI")
        self.setGeometry(100, 100, 600, 400)
        self.setMinimumSize(400, 300)
        
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(220, 220, 220))
        palette.setColor(QPalette.ButtonText, Qt.black)
        self.setPalette(palette)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_button = QPushButton("Seleccionar Directorio")
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(QLabel("Directorio:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        
        script_layout = QHBoxLayout()
        self.script_input = QLineEdit("/usr/bin/dir2rpm.sh")
        self.script_button = QPushButton("Seleccionar Script")
        self.script_button.clicked.connect(self.select_script)
        script_layout.addWidget(QLabel("Ruta del Script:"))
        script_layout.addWidget(self.script_input)
        script_layout.addWidget(self.script_button)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        tabs = QTabWidget()
        scroll_area.setWidget(tabs)
        
        meta_widget = QWidget()
        meta_layout = QVBoxLayout(meta_widget)
        self.package_name = QLineEdit()
        self.version = QLineEdit("1.0")
        self.release = QLineEdit("1")
        self.summary = QLineEdit("Binary package generated from directory")
        self.description = QTextEdit("Binary package generated from directory")
        self.description.setMaximumHeight(100)
        self.author = QLineEdit("xAI")
        self.license = QComboBox()
        self.license.addItems(["MIT", "GPL", "Apache", "BSD"])
        self.arch = QComboBox()
        self.arch.addItems(["noarch", "x86_64", "i386", "arm"])
        self.depends = QLineEdit()  # Nueva entrada para dependencias
        
        meta_layout.addWidget(QLabel("Nombre del Paquete:"))
        meta_layout.addWidget(self.package_name)
        meta_layout.addWidget(QLabel("Versión:"))
        meta_layout.addWidget(self.version)
        meta_layout.addWidget(QLabel("Release:"))
        meta_layout.addWidget(self.release)
        meta_layout.addWidget(QLabel("Sumario:"))
        meta_layout.addWidget(self.summary)
        meta_layout.addWidget(QLabel("Descripción:"))
        meta_layout.addWidget(self.description)
        meta_layout.addWidget(QLabel("Autor/Vendor:"))
        meta_layout.addWidget(self.author)
        meta_layout.addWidget(QLabel("Licencia:"))
        meta_layout.addWidget(self.license)
        meta_layout.addWidget(QLabel("Arquitectura:"))
        meta_layout.addWidget(self.arch)
        meta_layout.addWidget(QLabel("Dependencias (separadas por comas):"))  # Etiqueta para Depends
        meta_layout.addWidget(self.depends)  # Añadimos el campo de dependencias
        meta_layout.addStretch()
        
        scripts_widget = QWidget()
        scripts_layout = QVBoxLayout(scripts_widget)
        self.preinst = QTextEdit()
        self.preinst.setMaximumHeight(100)
        self.postinst = QTextEdit()
        self.postinst.setMaximumHeight(100)
        self.preun = QTextEdit()
        self.preun.setMaximumHeight(100)
        self.postun = QTextEdit()
        self.postun.setMaximumHeight(100)
        
        load_preinst_btn = QPushButton("Cargar Preinst")
        load_preinst_btn.clicked.connect(lambda: self.load_script(self.preinst))
        load_postinst_btn = QPushButton("Cargar Postinst")
        load_postinst_btn.clicked.connect(lambda: self.load_script(self.postinst))
        load_preun_btn = QPushButton("Cargar Preun")
        load_preun_btn.clicked.connect(lambda: self.load_script(self.preun))
        load_postun_btn = QPushButton("Cargar Postun")
        load_postun_btn.clicked.connect(lambda: self.load_script(self.postun))
        
        scripts_layout.addWidget(QLabel("Preinst Script:"))
        scripts_layout.addWidget(self.preinst)
        scripts_layout.addWidget(load_preinst_btn)
        scripts_layout.addWidget(QLabel("Postinst Script:"))
        scripts_layout.addWidget(self.postinst)
        scripts_layout.addWidget(load_postinst_btn)
        scripts_layout.addWidget(QLabel("Preun Script:"))
        scripts_layout.addWidget(self.preun)
        scripts_layout.addWidget(load_preun_btn)
        scripts_layout.addWidget(QLabel("Postun Script:"))
        scripts_layout.addWidget(self.postun)
        scripts_layout.addWidget(load_postun_btn)
        scripts_layout.addStretch()
        
        tabs.addTab(meta_widget, "Metadatos")
        tabs.addTab(scripts_widget, "Scripts")
        
        action_layout = QHBoxLayout()
        self.preview_button = QPushButton("Vista Previa SPEC")
        self.preview_button.clicked.connect(self.preview_spec)
        self.create_button = QPushButton("Crear RPM")
        self.create_button.clicked.connect(self.create_rpm)
        action_layout.addWidget(self.preview_button)
        action_layout.addWidget(self.create_button)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        
        layout.addLayout(dir_layout)
        layout.addLayout(script_layout)
        layout.addWidget(scroll_area)
        layout.addLayout(action_layout)
        layout.addWidget(QLabel("Salida:"))
        layout.addWidget(self.output_text)
        
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio")
        if directory:
            self.dir_input.setText(directory)
            default_name = os.path.basename(directory).lower().replace(' ', '-')
            self.package_name.setText(default_name)
    
    def select_script(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Seleccionar Script dir2rpm", "", "Shell Scripts (*.sh);;All Files (*)")
        if file_name:
            self.script_input.setText(file_name)
    
    def load_script(self, text_edit):
        file_name, _ = QFileDialog.getOpenFileName(self, "Cargar Script", "", "Shell Scripts (*.sh);;All Files (*)")
        if file_name:
            with open(file_name, 'r') as f:
                text_edit.setText(f.read())
    
    def generate_spec_content(self):
        package_name = self.package_name.text() or os.path.basename(self.dir_input.text()).lower().replace(' ', '-') or "default-package"
        version = self.version.text() or f"1.0.{os.popen('date +%Y%m%d').read().strip()}"
        release = self.release.text() or "1"
        summary = self.summary.text() or "Binary package generated from directory"
        description = self.description.toPlainText() or summary
        author = self.author.text() or "xAI"
        license = self.license.currentText() or "MIT"
        arch = self.arch.currentText() or "noarch"
        depends = self.depends.text()  # Obtener las dependencias
        preinst = self.preinst.toPlainText()
        postinst = self.postinst.toPlainText()
        preun = self.preun.toPlainText()
        postun = self.postun.toPlainText()
        
        spec_content = f"""Name: {package_name}
Version: {version}
Release: {release}
Summary: {summary}
License: {license}
Vendor: {author}
BuildArch: {arch}
"""
        if depends:
            spec_content += f"Requires: {depends}\n"  # Añadir Requires si hay dependencias
        
        spec_content += f"""
%description
{description}

%prep
# No preparation needed, using binaries directly

%build
# No build step

%install
rm -rf %{{buildroot}}/*
mkdir -p %{{buildroot}}
# Files will be copied here by the script

%files
# File list will be generated by the script during execution

"""
        if preinst:
            spec_content += "%pre\n" + preinst + "\n"
        if postinst:
            spec_content += "%post\n" + postinst + "\n"
        if preun:
            spec_content += "%preun\n" + preun + "\n"
        if postun:
            spec_content += "%postun\n" + postun + "\n"
        
        spec_content += f"""%changelog
* {os.popen('LC_TIME=C date "+%a %b %d %Y"').read().strip()} Juan Madrid <ecmadrid@github> - {version}-{release}
- Binary package generated automatically with GUI support
"""
        return spec_content
    
    def preview_spec(self):
        if not self.dir_input.text():
            self.output_text.append("Error: Selecciona un directorio primero")
            return
        spec_content = self.generate_spec_content()
        dialog = SpecPreviewDialog(spec_content, self)
        dialog.exec_()
    
    def create_rpm(self):
        input_dir = self.dir_input.text()
        if not input_dir or not os.path.isdir(input_dir):
            self.output_text.append("Error: Selecciona un directorio válido")
            return
        
        script_path = self.script_input.text()
        if not os.path.isfile(script_path):
            self.output_text.append(f"Error: El script '{script_path}' no existe")
            return
        
        current_dir = os.getcwd()
        args = ["/bin/bash", script_path, input_dir]
        
        metadata = []
        if self.package_name.text():
            metadata.append(f"Name: {self.package_name.text()}")
        if self.version.text():
            metadata.append(f"Version: {self.version.text()}")
        if self.release.text():
            metadata.append(f"Release: {self.release.text()}")
        if self.summary.text():
            metadata.append(f"Summary: {self.summary.text()}")
        if self.description.toPlainText():
            metadata.append(f"Description: {self.description.toPlainText()}")
        if self.author.text():
            metadata.append(f"Vendor: {self.author.text()}")
        if self.license.currentText():
            metadata.append(f"License: {self.license.currentText()}")
        if self.arch.currentText():
            metadata.append(f"Arch: {self.arch.currentText()}")
        if self.depends.text():  # Añadir dependencias al metadata
            metadata.append(f"Depends: {self.depends.text()}")
        
        if metadata:
            metadata_path = os.path.join(input_dir, "metadata.txt")
            with open(metadata_path, "w") as f:
                f.write("\n".join(metadata))
        
        scripts = {
            "preinst": self.preinst.toPlainText(),
            "postinst": self.postinst.toPlainText(),
            "preun": self.preun.toPlainText(),
            "postun": self.postun.toPlainText()
        }
        for script_name, content in scripts.items():
            if content.strip():
                with open(os.path.join(input_dir, script_name), "w") as f:
                    f.write(content)
        
        self.output_text.append(f"Ejecutando desde {current_dir}: {' '.join(args)}")
        try:
            process = subprocess.Popen(args, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True, 
                                    cwd=current_dir)
            stdout, stderr = process.communicate()
            
            package_name = self.package_name.text() or os.path.basename(input_dir).lower().replace(' ', '-')
            version = self.version.text() or f"1.0.{os.popen('date +%Y%m%d').read().strip()}"
            release = self.release.text() or "1"
            arch = self.arch.currentText() or "noarch"
            rpmbuild_dir = os.path.expanduser("~/rpmbuild")
            expected_rpm = f"{rpmbuild_dir}/RPMS/{arch}/{package_name}-{version}-{release}.{arch}.rpm"
            current_dir_rpm = os.path.join(current_dir, f"{package_name}-{version}-{release}.{arch}.rpm")
            
            if process.returncode == 0:
                self.output_text.append("Salida del script:\n" + stdout)
                self.output_text.append(f"Buscando RPM...")
                self.output_text.append(f"- Esperado en rpmbuild: {expected_rpm}")
                self.output_text.append(f"- Esperado en actual: {current_dir_rpm}")
                
                found = False
                if os.path.exists(expected_rpm):
                    self.output_text.append(f"Encontrado en {expected_rpm}. Moviendo al directorio actual...")
                    os.rename(expected_rpm, current_dir_rpm)
                    found = True
                elif os.path.exists(current_dir_rpm):
                    self.output_text.append(f"Encontrado en {current_dir_rpm}")
                    found = True
                else:
                    rpm_files = glob.glob(f"{rpmbuild_dir}/RPMS/*/*.rpm") + glob.glob("*.rpm")
                    if rpm_files:
                        self.output_text.append("RPMs encontrados en otras ubicaciones:")
                        for rpm in rpm_files:
                            self.output_text.append(f"- {rpm}")
                        found = True
                
                if found:
                    self.output_text.append("RPM localizado con éxito")
                else:
                    self.output_text.append("Error: No se encontró ningún RPM generado")
            else:
                self.output_text.append(f"Error (código {process.returncode}):\n" + stderr)
                self.output_text.append("Verifica el script o el entorno (¿rpmbuild instalado?)")
            
            self.output_text.append("Archivos temporales generados:")
            if metadata:
                self.output_text.append(f"- {metadata_path}")
            for script_name, content in scripts.items():
                if content.strip():
                    self.output_text.append(f"- {os.path.join(input_dir, script_name)}")
            self.output_text.append("Puedes inspeccionarlos y eliminarlos manualmente.")
                
        except Exception as e:
            self.output_text.append(f"Error al ejecutar el script: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Dir2RPMWindow()
    window.show()
    sys.exit(app.exec_())
