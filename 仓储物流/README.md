# 仓储物流项目

本目录包含一份可离线浏览的静态网站，以及可直接在 Obsidian 编辑的 Markdown 项目书源文件。

## 目录说明

- content：项目书正文源文件，建议在 Obsidian 中编辑。
- assets/style.css：网站样式源文件。
- build_site.py：仅使用 Python 标准库生成网站，无需安装第三方包。
- site/index.html：生成的网站首页。
- site/pages：各要点独立子网页。

## 生成和预览

在本目录运行：

    py -3 build_site.py

生成后可直接打开 site/index.html。也可以在本目录运行：

    py -3 -m http.server 8000 --directory site

然后访问 http://localhost:8000。编辑 content 下的 Markdown 后重新运行构建脚本即可更新网站。

## 项目边界

当前版本是立项与试点方案，不是已确认需求、正式报价或已经实现的软件。网页中的产品类型、仓库规模、设备和验收目标需要由实际仓库负责人补充确认。

项目书章节参考欧盟委员会 PM² 项目启动、商业论证、项目章程、工作计划和风险管理等项目管理工件；实际内容按小团队仓储试点缩编。资料链接集中见 content/references.md。
