---
title: Linux学习笔记
date: 2019-09-23 09:07:49
tags:
- Linux
categories: 学习笔记
---

## Linux常用命令

### 文件处理命令

---

> ls       // *list 显示目录文件*
>
> ls -a  // *显示所有文件，包括隐藏文件*
>
> ls -l   // *详细信息显示*
>
> ls -d  // *查看目录属性*

文件类型说明

<!--more-->

> -rw-r--r--  // *-开头代表文件 d为目录 l为软连接文件*
>
> rw- r-- r--  // *每三位是一个组别，依次为 u所有者 g所属组 o其他人*
>
> -rw-r--r--   // *r(read)表示读权限 w(write)写 权限 x(execute)执行权限*

---

> mkdir [目录]    // *make directiories 创建目录*
>
> mkdir -p [目录] // *递归创建目录*
>
> rmdir [目录]   // *remove empty directories 删除空目录*
>
> rm -rf [文件或目录] // *remove 删除文件 -r删除目录 -f强制执行*

---

> pwd // *print working directory 显示当前目录*
>
> cd [目录]    // *change directory 切换目录*
>
> cp -rp [原文件或目录] [目标目录]  // *copy 复制文件或目录 -r复制目录 -p保留属性*
>
> mv [原文件或目录] [目标目录/新名称]  // *move 剪切文件、改名*