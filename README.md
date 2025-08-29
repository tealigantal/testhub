# 科学计算器

该项目提供了一个科学计算库、命令行界面以及基于浏览器的前端。后端使用 Python 实现，并在 Docker 容器中运行。

## 安装与使用库

```bash
pip install -e .
```

在 Python 中使用：

```python
from scicalc import evaluate
print(evaluate("2 + 2"))
```

## 命令行计算器

```bash
scicalc
```

## Web 前端

项目内置一个简单的 HTTP 服务器，提供点击式计算器界面。

启动服务器：

```bash
python -m scicalc.web
```

访问 [http://localhost:8000](http://localhost:8000) 查看前端页面。

## Docker 运行

```bash
docker build -t scicalc .
docker run -p 8000:8000 scicalc
```

然后在浏览器中打开 `http://localhost:8000`。
