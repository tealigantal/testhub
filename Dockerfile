FROM python:3.12-slim
WORKDIR /app

# 先装依赖（利用缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir pytest

# 再拷贝源码
COPY . .

# 默认命令（CI里不会用到，compose 的 sut 会覆盖为 pytest）
EXPOSE 8000

# 默认运行内置的简易 HTTP 服务器，提供前端页面和计算接口
CMD ["python", "-m", "scicalc.web"]
