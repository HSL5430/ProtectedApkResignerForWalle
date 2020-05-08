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

def help():
  print ("\n**** =============================help=================================== ****\n")
  print ("①：使用config.py中配置的参数 -->  直接双击ApkResigner.py（如果本机安装并关联了Python Launcher可用）")
  print ("②：使用config.py中配置的参数 -->  终端执行python ApkResigner.py")
  print ("③：使用自定义参数 -->  终端执行python ApkResigner.py <androidBuildToolsPath> <channelsInputFilePath> <channelsOutputFilePath>")
  print ("    androidBuildToolsPath：android sdk中build-tools下某个版本的路径，尽量跟Android项目中的buildToolsVersion保持一致，如/Users/xxx/Library/Android/sdk/build-tools/28.0.3")
  print ("    channelsInputFilePath：渠道配置文件(.txt)和基础包所在的【目录】，默认当前脚本所在的目录")
  print ("    channelsOutputFilePath：渠道包输出的目录，默认当前脚本所在的目录下的channels文件夹")
  print ("    注意：这几个Path的结尾都不要带斜杠'/'")
  print ("\n**** =============================help=================================== ****\n")

if len(sys.argv) > 1:
  arg1 = sys.argv[1].lower()
  if "help" == arg1 or "h" == arg1:
    help()
    exit()

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

def getBuildToolsPath():
  if len(sys.argv) > 1 and len(sys.argv[1]) > 0:
    return sys.argv[1]
  else:
    return config.sdkBuildToolPath

#当前脚本文件所在目录
parentDir = curFileDir()
parentPath = parentDir + getBackslash()
os.chdir(parentDir)

def getChannelFilePath():
  if len(sys.argv) > 2 and len(sys.argv[2]) > 0:
    path = sys.argv[2] + getBackslash() + "channel.txt"
  elif len(config.channelFilePath) > 0:
    path = config.channelFilePath
  else:
    path = parentPath + "channel.txt"
  return path

def getChannelsInputFilePath():
  if len(sys.argv) > 2 and len(sys.argv[2]) > 0:
    path = sys.argv[2]
  elif len(config.protectedSourceApkDirPath) > 0:
    path = config.protectedSourceApkDirPath
  else:
    path = parentDir
  return path + getBackslash()

def getChannelsOutputFilePath():
  if len(sys.argv) > 3 and len(sys.argv[3]) > 0:
    path =  sys.argv[3]
  elif len(config.channelsOutputFilePath) > 0:
    path = config.channelsOutputFilePath
  else:
    path = parentPath + "channels"
  return path

#config
libPath = parentPath + "lib" + getBackslash()
buildToolsPath =  getBuildToolsPath() + getBackslash()
checkAndroidV2SignaturePath = libPath + "CheckAndroidV2Signature.jar"
walleChannelWritterPath = libPath + "walle-cli-all.jar"

keystorePath = os.path.abspath(config.keystorePath)
keyAlias = config.keyAlias
keystorePassword = config.keystorePassword
keyPassword = config.keyPassword

channelFilePath = getChannelFilePath()
channelsInputFilePath = getChannelsInputFilePath()
protectedSourceApkPath = channelsInputFilePath + config.protectedSourceApkName
channelsOutputFilePath = getChannelsOutputFilePath()

# 创建Channels输出文件夹
resetChannelsDir()

print ("\n**** =============================TASK BEGIN=================================== ****\n")
print ("\n↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓   zipalign -->  apksigner -->  writeChannelShell   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
print ("\n**** =============================TASK BEGIN=================================== ****\n")

apkFiles = getApkFiles(channelsInputFilePath)
if len(apkFiles) > 0:
  for apkFile in apkFiles:
    # 获取apkFile对应的channel文件:channel_[apkName].txt
    channelFile = channelsInputFilePath + "channel_" + apkFile.replace('apk','txt')
    if os.path.isfile(channelFile):
      channelFilePath = channelFile
    # 渠道信息存在，批量打包对应的渠道
    generateChannelApks(channelsInputFilePath + apkFile, channelFilePath)
else:
  # 默认配置
  generateChannelApks(protectedSourceApkPath, channelFilePath)

print ("\n**** =============================TASK FINISHED=================================== ****\n")
print ("\n↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓   Please check channels in the path   ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
print ("\n"+channelsOutputFilePath+"\n")
print ("\n**** =============================TASK FINISHED=================================== ****\n")
