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
	
	def __init__(self, chroot_path, package_list, parent=None):
		super(QtCore.QThread, self).__init__(parent)
		self.chroot_path = chroot_path
		self.package_list = package_list
	
	def run(self):
		self.sigCmdOutput.emit("Mounting <font color=green>/sys</font>, <font color=green>/proc</font> and <font color=green>/dev</font>!")
		try:
			subprocess.Popen("mount -t sysfs none "+self.chroot_path+"/sys", shell=True)
			subprocess.Popen("mount -t proc none "+self.chroot_path+"/proc", shell=True)
			subprocess.Popen("mount --rbind /dev "+self.chroot_path+"/dev", shell=True)
		except Exception as ex:
			self.sigCmdOutput.emit("CET: "+str(ex))
			pass
			
		
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
		self.sigCmdOutput.emit("<font color=green>Equo</font> log saved to <font color=green>CWD</font>")
		equo_log = open("equo_log", "w")
		equo_log.write(proc_stdout)
		self.sigCmdOutput.emit("Unmounting Devices!")
		proc = subprocess.Popen(['chroot', self.chroot_path, '/bin/bash'], stdout=subprocess.PIPE, 
															stdin=subprocess.PIPE,stderr=subprocess.STDOUT)
		proc_stdout = proc.communicate(input='umount {proc,sys,dev/pts,dev/shm,dev} && exit')[0]
		self.sigCmdOutput.emit(proc_stdout)
		self.sigCmdOutput.emit("Deployment finished!")


class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(QtGui.QWidget, self).__init__(parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		
		self.setupSignals()

		self.arch_path = "/rogentos/"
		self.package_list = None
		self.output_dir = None
		self.chroot_dir = None
		self.packages = []

		self.init_info()

                    
	def setupSignals(self):
		self.ui.ar_path_button.clicked.connect(self.archive_file_dialog)
		self.ui.file_inst_list_path.clicked.connect(self.package_file_dialog)
		self.ui.wdir_button.clicked.connect(self.working_dir_path)
		self.ui.begin_button.clicked.connect(self.begin_execution)

	def init_info(self):
		self.ui.textarea.append("<b><font size=5>Rogentos Chroot Deployment Tool</font></b><br>")
		self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Archive path is:</font> {0}</b>".format(self.arch_path)) 
		self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Package List path is:</font> {0} <font color=red>(Required)</font></b>".format(self.package_list))
		self.ui.textarea.append("<b><font color=blue> <font color=black>#!</font> Output dir path is:</font> {0} <font color=red>(Required)</font></b></b>".format(self.output_dir))
        
    
	def archive_file_dialog(self):
		arch_path = QtGui.QFileDialog.getOpenFileName(self, 'Archive Path', '.')
		if arch_path:
			self.ui.textarea.append("<b><font color=blue> <font color=black>>></font> Archive path:</font> {0}</b>".format(arch_path))
			self.arch_path = arch_path

	def package_file_dialog(self):
		package_path = QtGui.QFileDialog.getOpenFileName(self, 'Package List Path', '.')
		if package_path:
			self.ui.textarea.append("<b><font color=blue> <font color=black>>></font> Package List path:</font> {0}</b>".format(package_path))
			self.package_list = package_path
			with open(package_path) as pl:
				for line in pl:
					if line:
						self.packages.append(line)

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
			# Pass files that contain garbage in their path.
			pass
 
	def begin_execution(self):
		if self.package_list == None and self.output_dir == None:
			self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Please input <font color=red>Package List</font> path and <font color=red>Output Dir</font> path!</font></b>")
			return
		if os.path.isfile(self.arch_path) == False:
			self.ui.textarea.append("<b><font color=black><font color=red>!!</font> Invalid <font color=red>Archive</font> file!<b></font>")
			return
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
