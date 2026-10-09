FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
FROM nginx:1.27-alpine
RUN apk update && apk upgrade --no-cache
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN addgroup -S appgroup && adduser -S appuser -G appgroup \
  && mkdir -p /var/cache/nginx /var/log/nginx /var/run \
  && chown -R appuser:appgroup /usr/share/nginx/html /var/cache/nginx /var/log/nginx /var/run /etc/nginx/conf.d \
  && sed -i 's/user nginx;/user appuser;/' /etc/nginx/nginx.conf || true
USER appuser
EXPOSE 8080
