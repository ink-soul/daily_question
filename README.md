# daily_question

个人小玩具之一

爬取B站王道计算机教育的每日一题动态保存为markdawn文档

结果示例可在此查看[每日一题](https://www.inksoul.top/stuff/result/)

## 使用说明

初次运行请修改配置文件中`UPDATEMODE`的值为`false`，第二次及以后修改为`true`

如需要改变结果文档的路径请在配置文件中修改`RESULTFILEPATH`，建议使用相对路径

## 代码使用
如果你有一个自己的服务器，或是不会关机的电脑，可以通过如下方式使用代码。本项目使用Python3且建议使用环境管理工具设置单独环境。


1. 首先clone本仓库：

```bash
git clone https://github.com/ink-soul/daily_question.git
```

2. 安装依赖：

```bash
cd daily_question

pip3 install -r requirements.txt
```

3. 根据示例完成配置文件`UID`、 `UPDATEMODE`、 `RESULTFILEPATH`的配置可参考[使用说明](#使用说明)

4. 初次运行完成初始化
   
```bash

python3 dailyQuestion.py

```

5. 修改配置文件中`UPDATEMODE`为`true`

6. 配置文件完成后运行代码`timer.py`，即可实现每日定时更新：

```bash
python3 timer.py
```


