FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y snmp iputils-ping nginx && \
    rm -rf /var/lib/apt/lists/*

RUN pip install flask

WORKDIR /app

# Configure Nginx for Port 80 and API Proxy
RUN echo 'server { \
    listen 80; \
    location / { \
        root /var/www/html; \
        index index.html; \
        try_files $uri $uri/ =404; \
    } \
    location /api/ { \
        proxy_pass http://127.0.0.1:5000/; \
    } \
}' > /etc/nginx/sites-available/default

RUN echo "daemon off;" >> /etc/nginx/nginx.conf

COPY index.html /var/www/html/index.html
COPY extract.py .

RUN chmod -R 777 /var/www/html

RUN echo '#!/bin/bash\nnginx &\npython3 /app/extract.py' > /app/start.sh
RUN chmod +x /app/start.sh

CMD ["/app/start.sh"]
