#!/usr/bin/python
# -*- coding: utf-8 -*-
#
import getopt
import os
import shutil
import sys
import tarfile
import subprocess


class submod:
	def __init__(self):
		self.oldcom = ''
		self.newcom = ''
		self.sub_old_cmt = ""
		self.sub_new_cmt = ""
		self.path = ""
		self.sub_path = ""
		self.tarpath = ""
		self.module = ""

	def exec_shell(self, execmd, submdpath):
		os.chdir(submdpath)
		res = subprocess.Popen(execmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		pipe = res.stdout.readlines()
		return pipe

	def chk_sub(self, com):
		# check submodule exist and get submodule commit
		print("----------------------------------------------------------------------")
		cmd1 = "git pull | git checkout %s" % com
		print("[切换分支] ", com)
		self.exec_shell(cmd1, './')
		# 判断 .gitmodules 存在
		if os.path.exists('.gitmodules'):
			with open('.gitmodules', 'r') as f:
				data = f.readlines()
			# 判断 .gitmodules 中是否有需要得子模块
			if '[submodule "%s"]\n' % self.module in data:
				num = data.index('[submodule "%s"]\n' % self.module) + 1
				# 获取子模块目录位置
				self.sub_path = data[num].split('\n')[0].split()[-1]
				print("[submodule path] ", self.sub_path)
				# 更新当前 commit 指定的子模块
				cmd2 = "git submodule update --init --recursive %s" % self.module
				print("[cmd] ", cmd2)
				self.exec_shell(cmd2, './')
				# 查看指定子模块 commit
				cmd3 = 'git submodule status %s' % self.module
				data = self.exec_shell(cmd3, './')
				res = data[0].decode().split('\n')[0].split()[0][-40:]
				print("Commit %s Submodule commit is: %s" % (com, res))
				return res
		else:
			print("The current commit has no submodule")
			return "0" * 40

	def main_repo(self):
		print("----------------------------------------------------------------------")
		print("[*] main file archive")
		tmpath = "latest_%s" % self.newcom[0:8]
		self.tarpath = os.path.join(self.path + tmpath)
		print("[tarpath] ", self.tarpath)
		if os.path.exists(self.tarpath): shutil.rmtree(self.tarpath)
		tarname = self.tarpath + '.tar.gz'
		chkcmd = 'git pull | git diff --name-only --diff-filter=ARMC {1}..{0}'.format(self.newcom, self.oldcom)
		if len(self.exec_shell(chkcmd, './')) == 0:
			print("[*] none file")
		else:
			cmd = 'git archive -o {0} {1} $(git diff --name-only --diff-filter=ARMC {2}..{1})'.format(tarname, self.newcom, self.oldcom)
			print("[cmd] ", cmd)
			self.exec_shell(cmd, './')
			self.tar_file(tarname, self.tarpath)
			print("[*] git archive commit file success")

	def sub_repo(self, path):
		if self.sub_old_cmt == self.sub_new_cmt:
			# old and new ["0*40, abc***"]
			print("[*] submodule no change")
		elif self.sub_old_cmt != "0" * 40 and self.sub_new_cmt == "0" * 40:
			print("[*] submodule delete")
		elif self.sub_old_cmt == "0" * 40 and self.sub_new_cmt != "0" * 40:
			# old, new ["0*40 aaa***", "bbb*** 0*40", "ccc*** ddd***"]
			print("----------------------------------------------------------------------")
			print("[*] Submodule %s %s..%s" % (self.module, self.sub_old_cmt, self.sub_new_cmt))
			print("----------------------------------------------------------------------")
			print("[*] submodule file archive")
			tarname = os.path.join(self.tarpath, path, 'sub_%s.tar.gz' % path)
			tarpath = os.path.join(self.tarpath, path)
			print("[tarname] ", tarname)
			if self.sub_old_cmt != "0"*40 and self.sub_new_cmt != "0"*40:
				sub_cmd = 'git archive -o {0} {1} $(git diff --name-only --diff-filter=ARMC {2}..{1})'.format(tarname, self.sub_new_cmt, self.sub_old_cmt)
			elif self.sub_old_cmt == "0"*40 and self.sub_new_cmt != "0"*40:
				sub_cmd = 'git archive --format tar.gz --output %s %s' % (tarname, self.sub_new_cmt)
			print("[cmd] ", sub_cmd)
			self.exec_shell(sub_cmd, path)
			self.tar_file(tarname, tarpath)
			print("[*] git archive commit file success")
		print("----------------------------------------------------------------------")

	def tar_file(self, tarname, path):
		if os.path.isfile(tarname):
			untar = tarfile.open(tarname)
			names = untar.getnames()
			for name in names:
				untar.extract(name, path)
			untar.close()
		os.remove(tarname)

	def process(self):
		# main archive and tar
		self.main_repo()
		# submodule commit
		self.sub_old_cmt = self.chk_sub(self.oldcom)
		self.sub_new_cmt = self.chk_sub(self.newcom)
		# submodule archive
		self.sub_repo(self.sub_path)

	def main(self, argv):
		opts, args = getopt.getopt(argv, '-h', ['help', 'oldcom=', 'newcom=', 'module=', 'outpath='])
		for opt, arg in opts:
			if opt in ['-h', '--help']:
				pass
			elif opt == '--oldcom':
				self.oldcom = arg
			elif opt == '--newcom':
				self.newcom = arg
			elif opt == '--module':
				self.module = arg
			elif opt == '--tarpath':
				self.path = arg
		self.process()


if __name__ == '__main__':
	sub = submod()
	sub.main(sys.argv[1:])
