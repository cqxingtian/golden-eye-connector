FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 监听所有网卡；端口由平台运行时注入 PORT（Render/Railway 都会注入），
# 这里故意不写死 PORT，避免覆盖平台注入值。本地未注入时应用默认 8787。
ENV HOST=0.0.0.0
EXPOSE 8787
CMD ["python", "mcp_server.py"]
