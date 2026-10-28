FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# 监听所有网卡，便于容器/云部署
ENV HOST=0.0.0.0 PORT=8787
EXPOSE 8787
CMD ["python", "mcp_server.py"]
