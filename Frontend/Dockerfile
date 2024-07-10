# Use the Nginx image from Docker Hub
FROM nginx:alpine

# Remove the default nginx index page
RUN rm /usr/share/nginx/html/index.html

# Copy the static content (HTML, CSS, JS) to the Nginx server
COPY . /usr/share/nginx/html

# Expose port 80 to the Docker host, so we can access the Nginx server
EXPOSE 80

# Start Nginx when the container has provisioned.
CMD ["nginx", "-g", "daemon off;"]