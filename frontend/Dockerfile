# Use official Node.js image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy all source code
COPY . .

# Expose port (Vite default)
EXPOSE 5173

# Command to run development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

