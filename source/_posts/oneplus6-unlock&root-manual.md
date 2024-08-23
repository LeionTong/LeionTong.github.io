---
title: oneplus6解锁并root教程
date: 2018-05-17T00:00:00.000Z
tags: oneplus
---
# oneplus6解锁并root教程

## 1. 打开开发者模式，允许解锁设备

版本号连续点好多次，可以打开开发者模式，进入开发者模式，选中“允许OEM解锁设备”。

## 2. 解锁

`fastboot oem unlock`

## 3. 启动 twrp-3.2.1-0-enchilada.img 临时recovery镜像

`fastboot boot twrp-3.2.1-0-enchilada.img`

<!-- more -->
## 4. 推送 TWRP 安装包

`adb push twrp-installer-enchilada-3.2.1-0.zip /sdcard`

## 5.刷入 twrp-installer-enchilada-3.2.1-0.zip 永久recovery 安装包

点击按钮 Install，选中 /sdcard/twrp-installer-enchilada-3.2.1-0.zip，滑动滑块进行安装。

## 6. 进入 TWRP recovery 模式


执行命令`fastboot reboot recovery`，或者点击按钮 Reboot，Recovery，重启至recovery模式。

## 7. 推送 Magisk 安装包

`adb push {Magisk-v16.0.zip,MagiskManager-v5.7.0.apk} /sdcard`

## 8. 刷入 Magisk 安装包

点击按钮 Install，选中 /sdcard/Magisk-v16.0.zip，滑动滑块进行安装。

## 9. 重启系统

