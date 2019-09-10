#!/usr/bin/python  
#-*-coding:utf-8-*-

# /**
#  * ================================================
#  * 作    者：JayGoo
#  * 版    本：1.0.1
#  * 更新日期：2017/12/29
#  * 邮    箱: 1015121748@qq.com
#  * ================================================
#  */

import os
import sys
import config
import platform
import shutil

#获取脚本文件的当前路径
def curFileDir():
     #获取脚本路径
     path = sys.path[0]
     #判断为脚本文件还是py2exe编译后的文件，
     #如果是脚本文件，则返回的是脚本的目录，
     #如果是编译后的文件，则返回的是编译后的文件路径
     if os.path.isdir(path):
         return path
     elif os.path.isfile(path):
         return os.path.dirname(path)

#判断当前系统
def isWindows():
  sysstr = platform.system()
  if("Windows" in sysstr):
    return 1
  else:
    return 0

#兼容不同系统的路径分隔符
def getBackslash():
	if(isWindows() == 1):
		return "\\"
	else:
		return "/"

# 重置Channels输出文件夹
def resetChannelsDir():
  try:
    if os.path.isdir(channelsOutputFilePath):
      # 清空渠道信息
      shutil.rmtree(channelsOutputFilePath)
    # 创建Channels输出文件夹
    os.makedirs(channelsOutputFilePath)
    pass
  except Exception:
    pass

#遍历当前目录下的apk文件
def getApkFiles(dirname, ext='.apk'):
    """获取目录下所有特定后缀的文件
    @param dirname: str 目录的完整路径
    @param ext: str 后缀名, 以点号开头
    @return: list(str) 所有子文件名(不包含路径)组成的列表
    """
    return list(filter(
      lambda filename: os.path.splitext(filename)[1] == ext,
      os.listdir(dirname)))

# 生产渠道包
def generateChannelApks(apkFilePath, channelFilePath):
  print ("**** apkFilePath:" + apkFilePath + " ****")
  print ("**** channelFilePath:" + channelFilePath + " ****")
  zipalignedApkPath = apkFilePath[0 : -4] + "_aligned.apk"
  signedApkPath = zipalignedApkPath[0 : -4] + "_signed.apk"
  
  #对齐
  zipalignShell = buildToolsPath + "zipalign -v 4 " + apkFilePath + " " + zipalignedApkPath
  os.system(zipalignShell)
  
  #签名
  signShell = buildToolsPath + "apksigner sign --ks "+ keystorePath + " --ks-key-alias " + keyAlias + " --ks-pass pass:" + keystorePassword + " --key-pass pass:" + keyPassword + " --out " + signedApkPath + " " + zipalignedApkPath
  os.system(signShell)
  print(signShell)
  
  #检查V2签名是否正确
  checkV2Shell = "java -jar " + checkAndroidV2SignaturePath + " " + signedApkPath
  os.system(checkV2Shell)
  
  #写入渠道
  if len(config.extraChannelFilePath) > 0:
    writeChannelShell = "java -jar " + walleChannelWritterPath + " batch2 -f " + config.extraChannelFilePath + " " + signedApkPath + " " + channelsOutputFilePath
  else:
    writeChannelShell = "java -jar " + walleChannelWritterPath + " batch -f " + channelFilePath + " " + signedApkPath + " " + channelsOutputFilePath
  
  os.system(writeChannelShell)
  
  try:
    os.remove(zipalignedApkPath)
    os.remove(signedApkPath)
  finally:
    return

#当前脚本文件所在目录
parentDir = curFileDir()
parentPath = parentDir + getBackslash()

#config
libPath = parentPath + "lib" + getBackslash()
buildToolsPath =  config.sdkBuildToolPath + getBackslash()
checkAndroidV2SignaturePath = libPath + "CheckAndroidV2Signature.jar"
walleChannelWritterPath = libPath + "walle-cli-all.jar"
keystorePath = config.keystorePath
keyAlias = config.keyAlias
keystorePassword = config.keystorePassword
keyPassword = config.keyPassword
channelsOutputFilePath = parentPath + "channels"
channelFilePath = parentPath +"channel.txt"
protectedSourceApkPath = parentPath + config.protectedSourceApkName

# 检查自定义路径，并作替换
if len(config.protectedSourceApkDirPath) > 0:
  protectedSourceApkPath = config.protectedSourceApkDirPath + getBackslash() + config.protectedSourceApkName

if len(config.channelsOutputFilePath) > 0:
  channelsOutputFilePath = config.channelsOutputFilePath

if len(config.channelFilePath) > 0:
  channelFilePath = config.channelFilePath

# 创建Channels输出文件夹
resetChannelsDir()

print ("\n**** =============================TASK BEGIN=================================== ****\n")
print ("\n↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓   zipalign -->  apksigner -->  writeChannelShell   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
print ("\n**** =============================TASK BEGIN=================================== ****\n")

apkFiles = getApkFiles(parentPath)
if len(apkFiles) > 0:
  for apkFile in apkFiles:
    # 获取apkFile对应的channel文件:channel_[apkName].txt
    channelFile = parentPath + "channel_" + apkFile.replace('apk','txt')
    if os.path.isfile(channelFile):
      channelFilePath = channelFile
    # 渠道信息存在，批量打包对应的渠道
    generateChannelApks(parentPath + apkFile, channelFilePath)
else:
  # 默认配置
  generateChannelApks(protectedSourceApkPath, channelFilePath)

print ("\n**** =============================TASK FINISHED=================================== ****\n")
print ("\n↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓   Please check channels in the path   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
print ("\n"+channelsOutputFilePath+"\n")
print ("\n**** =============================TASK FINISHED=================================== ****\n")
