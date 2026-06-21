
FROM node:20-alpine AS build
WORKDIR /app

# Copy package files first to cache the npm install layer
COPY package*.json ./
RUN npm ci

# Copy source and build
COPY . .
RUN npx vite build


FROM nginx:alpine
WORKDIR /usr/share/nginx/html


RUN rm -rf ./*


COPY --from=build /app/dist .


COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
