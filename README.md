# 科学计算器

一个包含科学计算核心库、命令行工具以及基于浏览器前端的示例项目。项目支持常见的科学函数，既可本地运行，也可通过 Docker 部署。

## 功能概览
- `scicalc.evaluate` 函数可安全地计算字符串表达式，支持 `sin`、`cos`、`tan`、`pi`、幂运算等常用功能。
- 提供交互式命令行工具 `scicalc`。
- 内置 HTTP 服务器暴露 `/api/evaluate` 接口，并提供可点击的 Web 计算器界面。

## 安装与使用库
```bash
pip install -e .
```

在 Python 中调用：
```python
from scicalc import evaluate
print(evaluate("sin(pi/2)"))
```

## 命令行
```bash
scicalc
```

## Web 前端
启动轻量级 Web 服务器：
```bash
python -m scicalc.web
```
打开 [http://localhost:8000](http://localhost:8000) 后，可通过按钮输入表达式并按 `=` 计算。

## Docker 运行
```bash
docker build -t scicalc .
docker run -p 8000:8000 scicalc
```
容器启动后同样访问 `http://localhost:8000`。

## 测试
在本地运行单元测试：
```bash
PYTHONPATH=src pytest -q
```
也可以使用 Docker Compose 在隔离环境下运行：
```bash
docker compose -f compose.test.yml build
docker compose -f compose.test.yml run --rm sut
```
