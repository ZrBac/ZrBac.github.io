---
title: Git 操作指南
date: 2019-11-25 17:46:16
tags: 
- Git
categories: 学习笔记
---


## Git基础教程

### Git 核心思想

- 工作区(Workspace): 电脑中的实际目录
- 暂存区(Index): 类似于缓存区，临时保存改动
- 仓库区(Repository): 分为本地和远程仓库
- 代码提交步骤: `git add`, `git commit`, `git push`


### Git 基本操作

#### 初始化

```git
# 在当前目录新建一个Git代码库
$ git init

# 下载一个项目和它的整个代码历史 [Git only]

$ git clone <url>
```

#### 配置

```git
# 列举所有配置
$ git config -l

# 为命令配置别名
$ git config --global alias.co checout
$ git config --global alias.ci commit
$ git config --global alias.st status
$ git config --global alias.br branch

# 设置提交代码时的用户信息
$ git config --global user.name "your name"
$ git config --global user.email " your email address"
```

#### 增删文件

```git
# 添加当前目录的所有文件到暂存区
$ git add .

# 添加指定文件到暂存区
$ git add <file1> <file2> ...

# 添加指定目录到暂存区，包括子目录
$ git add <dir>

# 删除工作区文件，并将这次删除放入暂存区
$ git rm <file1> <file2> ...

# 停止追踪指定文件，但该文件会保存在工作区
$ git rm --cached <file>

# 文件改名，并将改名操作放入暂存区
$ git mv <file-original> <file-changed> 
```

#### 分支相关

```git
# 列出所有本地分支
$ git branch

# 列出所有本地分支和远程分支
$ git branch -a

# 新建分支，但依旧停留在当前分支区域
$ git branch <branch-name>

# 新建分支，并切换到新建分支(checkout或switch)
$ git checkout/switch -b <branch-name>

# 切换到指定分支(checkout或switch)
$ git checkout/switch <branch-name>

# 合并指定分支到当前分支
$ git merge <branch-name>

# 删除分支
$ git branch -d <branch-name>
```

#### 提交相关
```git
# 提交暂存区到仓库区
$ git commit -m <"your description">

# 提交工作区和暂存区变化到仓库去
$ git commit -a

# 提交时显示所有diff信息
$ git commit -v

# 提交暂存区修改到仓库去，合并到上次修改，并修改上次提交信息
$ git commit --amend -m <"your description">

# 上传本地分支到远程仓库
$ git push origin <branch-name>
```

#### 撤销操作

```git
# 恢复暂存区的指定文件到工作区
$ git checkout -- <file>

# 恢复暂存区当前目录所有文件到工作区
$ git checkout -- .

# 重置暂存区指定文件，但与上次commit保持一致，工作区不变
$ git reset <file>

# 重置暂存区与工作区，与上次commit一致
$ git reset --hard
```

#### 查询操作

```git
# 查看工作区文件修改状态
$ git status

# 查看工作区文件修改具体内容
$ git diff <file>

# 查看暂存区文件修改内容
$ git diff --cached <file>

# 查看版本库修改记录
$ git log

# 查看版本库修改记录
$ git log

# 查看某人提交记录
$ git log --author=someone

# 查看某个文件的历史具体修改内容
$ git log -p <file>

# 查看某次提交的具体修改内容
$ git show <commitID>