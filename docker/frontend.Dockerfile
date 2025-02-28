# Stage 1: Build React application
FROM node:18-alpine as build

WORKDIR /app

# Copy package.json and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build the React application
RUN npm run build

# Stage 2: Serve the built application with Nginx
FROM nginx:alpine

# Copy the built app to Nginx serve directory
COPY --from=build /app/build /usr/share/nginx/html

# Copy Nginx configuration
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"] 