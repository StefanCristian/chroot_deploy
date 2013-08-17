# -*- coding: utf-8 -*-

import sys
import shutil
import subprocess
import os
import tarfile

import sip
sip.setapi("QString", 2)

from PyQt4 import QtCore, QtGui
from main_ui import Ui_MainWindow

ROGENTOS_DEFAULT_ARCHIVE_NAME = ["Rogentos_Server_x86", "Rogentos_Server_x64"]
ROGENTOS_DEFAULT_SCRIPT_NAME = "chroot_cfg.sh"

class ArchiveExtract(QtCore.QThread):
    sigFinished = QtCore.pyqtSignal(int)
    sigProgress = QtCore.pyqtSignal(str, int)

    def __init__(self, path, opath, parent=None):
        super(QtCore.QThread, self).__init__(parent)
        
        self.path = path
        self.output_path = opath


    def run(self):
        shutil.rmtree(self.output_path)
        os.makedirs(self.output_path)

        archive = open(self.path, 'rb')     
        tar = tarfile.open(fileobj=archive,  encoding='utf8')

        for file in tar.getmembers():
            self.sigProgress.emit(file.name, file.size)
            try:
                tar.extract(file, self.output_path)
            except UnicodeDecodeError:
                # Pass files that contain garbage in their path.
                continue
        tar.close()
        self.sigFinished.emit(0)


class ChrootEnvThread(QtCore.QThread):
    sigCmdOutput = QtCore.pyqtSignal(str)
    
    def __init__(self, chroot_path, package_list, shpath=None, parent=None):
        super(QtCore.QThread, self).__init__(parent)

        self.chroot_path = chroot_path
        self.package_list = package_list

        self.shell_script = False
        self.script_name = None

        if shpath:
            self.script_name = "chroot_cfg.sh"
            shutil.copyfile(shpath, self.chroot_path+'/'+self.script_name)
            self.shell_script = True
    
    def run(self):
        self.sigCmdOutput.emit("Mounting <font color=green>/sys</font>, <font color=green>/proc</font> and <font color=green>/dev</font>!")
        try:
            subprocess.Popen("mount -t sysfs /sys "+self.chroot_path+"/sys", shell=True)
            subprocess.Popen("mount -t proc /proc "+self.chroot_path+"/proc", shell=True)
            subprocess.Popen("mount --bind /dev "+self.chroot_path+"/dev", shell=True)
        except Exception as ex:
            self.sigCmdOutput.emit("Failed to <font color=red>Unmount</font> the <font color=red>proc, dev and sys</font>")
            self.sigCmdOutput.emit("CET: "+str(ex))
            return
            
        self.sigCmdOutput.emit("Entered Chroot Environment!")
        self.sigCmdOutput.emit("Exec: <font color=green>env-update<font>!")
        proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
                                                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
        proc_stdout = proc.communicate(input='env-update && exit')[0]
        self.sigCmdOutput.emit(proc_stdout)
        self.sigCmdOutput.emit("Exec: <font color=green>source /etc/profile</font>")
        proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
                                                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
        proc_stdout = proc.communicate(input='source /etc/profile && exit')[0]
        self.sigCmdOutput.emit(proc_stdout)
        self.sigCmdOutput.emit("Exec: <font color=green>equo update</font> && <font color=green>equo repo mirrorsort</font>")
        proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
                                                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
        proc_stdout = proc.communicate(input='equo repo mirrorsort sabayonlinux.org && equo update && exit')[0]
        self.sigCmdOutput.emit("Adding <font color=green>packages</font> to the <font color=green>chroot environment</font>!")
        proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
                                                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
        proc_stdout = proc.communicate(input='equo install '+' '.join(self.package_list)+' && exit')[0]
        self.sigCmdOutput.emit("<font color=green>Equo</font> log saved to <font color=green>/var/log/equo.log</font>")
        equo_log = open("/var/log/equo.log", "w")
        equo_log.write(proc_stdout)
        if self.shell_script:
                        self.sigCmdOutput.emit("Executing bash script in chroot environment!")
                        proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
                                                                            stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
                        proc_stdout = proc.communicate(input='chmod +x /'+self.script_name+' && sh /'+self.script_name+' && exit')[0]

        
        self.sigCmdOutput.emit("Unmounting <font color=red>proc, dev and sys</font>!")
        try:
            subprocess.Popen('umount -n -l '+ self.chroot_path+'{/proc,/sys,/dev}', shell=True)
        except Exception as ex:
            self.sigCmdOutput.emit("Failed to <font color=red>Unmount</font> the <font color=red>proc, dev and sys</font>")
            self.sigCmdOutput.emit(str(ex))
            return      
        self.sigCmdOutput.emit("Deployment finished!")


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(QtGui.QWidget, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.setupSignals()
        
        self.default_path = True
        self.shell_script = False
        self.default_sh_script_path = True

        self.arch_path = "/rogentos/"
        
        self.package_list = None
        self.shell_script_path = None
        self.output_dir = None
        self.chroot_dir = None
        
        self.packages = []

        self.init_info()

                    
    def setupSignals(self):
        self.ui.ar_path_button.clicked.connect(self.archive_file_dialog)
        self.ui.file_inst_list_path.clicked.connect(self.package_file_dialog)
        self.ui.wdir_button.clicked.connect(self.working_dir_path)
        self.ui.begin_button.clicked.connect(self.begin_execution)
        self.ui.sh_script_btn.clicked.connect(self.sh_script_path)

    def init_info(self):
        self.ui.textarea.append("<b><font size=5>Rogentos Chroot Deployment Tool</font></b><br>")
        self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Archive path is:</font> {0}</b>".format(self.arch_path)) 
        self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Package List path is:</font> {0} <font color=red>(Required)</font></b>".format(self.package_list))
        self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Shell Script path is:</font> {0} <font color=red>(Optional)</font></b>".format(self.shell_script_path))
        self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Output dir path is:</font> {0} <font color=red>(Required)</font></b></b>".format(self.output_dir))
        
    
    def archive_file_dialog(self):
        arch_path = QtGui.QFileDialog.getOpenFileName(self, 'Archive Path', '.')
        if arch_path:
            self.ui.textarea.append("<b><font color=blue> <font color=black>>></font> Archive path:</font> {0}</b>".format(arch_path))
            self.arch_path = arch_path
            self.default_path = False

    def package_file_dialog(self):
        package_path = QtGui.QFileDialog.getOpenFileName(self, 'Package List Path', '.')
        if package_path:
            self.ui.textarea.append("<b><font color=blue> <font color=black>>></font> Package List path:</font> {0}</b>".format(package_path))
            self.package_list = package_path
            with open(package_path) as pl:
                for line in pl:
                    if line:
                        self.packages.append(line)
    def sh_script_path(self):
                shell_script = QtGui.QFileDialog.getOpenFileName(self, 'Bash Script Path')
                if shell_script:
                    self.ui.textarea.append("<b><font color=black> >> Custom <font color=green>BASH</font> script path: </font> {0} </b>".format(shell_script))
					self.default_sh_script_path = False
                    self.shell_script_path = shell_script
                    self.shell_script = True

    def working_dir_path(self):
        working_dir_path = QtGui.QFileDialog.getExistingDirectory(self, 'Working Directory Path')
        if working_dir_path:
            self.ui.textarea.append("<b><font color=blue> <font color=black>>></font> Output dir path:</font> {0}</b>".format(working_dir_path))
            self.ui.textarea.append("<b><font color=black> <font color=red>!!</font> Warning folder content will be <font color=red> erased</font></font>!</b>")
            
            self.output_dir = working_dir_path
            
    def chroot_callback(self, message):
        if message:
            self.ui.textarea.append("<b><font color=black> >> "+message+" </font></b>")
           
    def chroot_setup(self, status):
        if status == 0:
            self.ui.textarea.append("<b><font color=black> >> Extraction feinished <font color=green>successefully</font>!</font></b>")
            self.ui.statusbar.showMessage("#! Extraction complete!", 15)
            self.ui.textarea.append("<b><font color=black>#! Checking <font color=red>extracted</font> files!</font></b>")
            
            for name in os.listdir(self.output_dir):
                if os.path.isdir(os.path.join(self.output_dir, name)):
                    self.chroot_dir = os.path.join(self.output_dir, name)

            if os.path.isdir(self.chroot_dir+"/dev"):
                self.ui.textarea.append("<b><font color=black>>> Found <font color=green>dev</font> !</font></b>")
            else:
                self.ui.textarea.append("<b><font color=black>>> Cannot find <font color=red>dev</font> please check the archive!</font></b>")
                return
            if os.path.isdir(self.chroot_dir+"/proc"):
                self.ui.textarea.append("<b><font color=black>>> Found <font color=green>proc</font> !</font></b>")
            else:
                self.ui.textarea.append("<b><font color=black>>> Cannot find <font color=red>proc</font> please check the archive!</font></b>")
                return
            if os.path.isdir(self.chroot_dir+"/sys"):
                self.ui.textarea.append("<b><font color=black>>> Found <font color=green>sys</font> !</font></b>")
            else:
                self.ui.textarea.append("<b><font color=black>>> Cannot find <font color=red>sys</font> please check the archive!</font></b>")
                return
            
            self.ui.textarea.append("<b><font color=black> #! Setting up <font color=green>Gentoo chroot</font> environment!<b></font>")

            if self.shell_script:
                self.chroot_worker = ChrootEnvThread(self.chroot_dir, self.packages, self.shell_script_path)
            else:
                self.chroot_worker = ChrootEnvThread(self.chroot_dir, self.packages)

            self.chroot_worker.sigCmdOutput[str].connect(self.chroot_callback)
            
            if not self.chroot_worker.isRunning():
                self.chroot_worker.start()

        else:
            self.ui.textarea.append("<b><font color=red> >> Something went wrong while extracting files!</font></b>")
            self.ui.statusbar.showMessage("#! Extraction failed!", 0)
            return
        
     
    def progress_callback(self, filename, size):
        try:
            self.ui.statusbar.showMessage("#! Now extracting: {0} size: {1}b".format(filename, size), 0)
        except UnicodeEncodeError:
            # pass paths with garbage in their path
            pass
 
    def begin_execution(self):
        if self.package_list == None and self.output_dir == None:
            self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Please input <font color=red>Package List</font> path and <font color=red>Output Dir</font> path!</font></b>")
            return
            
        if self.default_path:
            if os.path.isfile(self.arch_path+ROGENTOS_DEFAULT_ARCHIVE_NAME[0]) == False:
                self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Archive 'Rogentos_Server_x86' not found in <font color=red>/rogentos/</font>!<b></font>")
                if os.path.isfile(self.arch_path+ROGENTOS_DEFAULT_ARCHIVE_NAME[1]) == False:
                        self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Archive 'Rogentos_Server_x64' not found in <font color=red>/rogentos/</font>!<b></font>")
                        return
                else:
                    self.arch_path = self.arch_path+ROGENTOS_DEFAULT_ARCHIVE_NAME[1]
                                       
            else:
                self.arch_path = self.arch_path+ROGENTOS_DEFAULT_ARCHIVE_NAME[0]         
        else:
            if os.path.isfile(self.arch_path) == False:
                self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Please input the <font color=red>Archive</font> path!</font></b>")
                return
            
        if self.default_sh_script_path == True:
            if os.path.isfile("/rogentos/"+ROGENTOS_DEFAULT_SCRIPT_NAME) == False:
                self.ui.textarea.append("<b><font color=black><font color=red>!! </font> /rogentos/"+ROGENTOS_DEFAULT_SCRIPT_NAME+" not found skipping!")
            else:
                self.shell_script_path = "/rogentos/"+ROGENTOS_DEFAULT_SCRIPT_NAME
                self.shell_script = True  
                
            
        if os.path.isfile(self.package_list) == False:
            self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Invalid <font color=red>Package List</font> file!</b>")
            return
            
        if os.path.isdir(self.output_dir) == False:
            self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Invalid <font color=red>Output</font> directory!</b>")
            return
        
        
        self.ui.textarea.append("<b><font color=black>#!</font><font color=green>Starting deployment!</font></b>")
        self.archive_worker = ArchiveExtract(self.arch_path, self.output_dir)
        self.archive_worker.sigProgress[str,int].connect(self.progress_callback)
        self.archive_worker.sigFinished[int].connect(self.chroot_setup)
        

        
        if not self.archive_worker.isRunning():
            self.ui.textarea.append("<b><font color=black> #! Archive <font color=green>Decompression</font> started!</font></b>")
            self.archive_worker.start()
            self.ui.textarea.append("<b><font color=black> >> Scanning archive <font color=green>files</font>, please wait.<font></b>")
            


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(460, 300)
    window.show()
    sys.exit(app.exec_())
