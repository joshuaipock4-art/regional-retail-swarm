# Production Dockerfile for 9-State Regional Retail Swarm
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    supervisor \
    bash \
    curl \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python web dependencies
RUN pip3 install fastapi uvicorn requests ShopifyAPI stripe

# Set working directory
WORKDIR /idm

# Copy the source folders explicitly
COPY idm/ /idm/
COPY core_engine.py /idm/
COPY agent_0_trend.py /idm/
COPY agent_1_source.py /idm/
COPY agent_4_storefront.py /idm/

# Ensure log directory exists
RUN mkdir -p /idm/system/logs

# Link supervisor configs
RUN ln -s /idm/system/supervisor/*.conf /etc/supervisor/conf.d/

# Expose Storefront Agent (Agent 4) port
EXPOSE 8080

# Set environment variables
ENV SWARM_ENV=production
ENV LOG_DIR=/idm/system/logs
ENV PYTHONUNBUFFERED=1

# Entrypoint: Start supervisor in foreground
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
