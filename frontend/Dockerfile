FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:1.27-alpine
RUN apk update && apk upgrade --no-cache
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
# BACKEND_HOST default matches the Docker Compose service name, so
# `docker compose up --build` works with no extra config.
# NGINX_ENVSUBST_FILTER limits substitution to our vars only, protecting
# nginx-native variables ($uri, $host, ...) from being clobbered.
ENV BACKEND_HOST=backend
ENV DNS_RESOLVER=127.0.0.11
RUN rm -f /etc/nginx/conf.d/default.conf \
  && addgroup -S appgroup && adduser -S appuser -G appgroup \
  && mkdir -p /var/cache/nginx /var/log/nginx /var/tmp/nginx /tmp/nginx \
  && chown -R appuser:appgroup /usr/share/nginx/html /var/cache/nginx /var/log/nginx /var/tmp/nginx /tmp/nginx /etc/nginx/conf.d \
  && sed -i 's|pid .*|pid /tmp/nginx/nginx.pid;|' /etc/nginx/nginx.conf || echo 'pid /tmp/nginx/nginx.pid;' >> /etc/nginx/nginx.conf
USER appuser
EXPOSE 8080
STOPSIGNAL SIGQUIT
CMD ["nginx", "-g", "daemon off;"]
