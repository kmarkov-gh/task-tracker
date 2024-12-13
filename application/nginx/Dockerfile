FROM nginx:alpine

# Копируем конфигурацию NGINX
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем статические файлы
COPY ./static/ /usr/share/nginx/html
