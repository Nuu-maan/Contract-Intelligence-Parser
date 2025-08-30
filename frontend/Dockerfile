# Build stage
FROM node:18-alpine as builder

WORKDIR /app

# Copy package files first for better layer caching
COPY package*.json ./
COPY pnpm-lock.yaml* ./
COPY next.config.js ./

# Install pnpm and dependencies
RUN npm install -g pnpm
# Install dependencies
RUN pnpm install

# Copy the rest of the application
COPY . .

# Build the application
RUN pnpm run build

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY package.json ./
COPY next.config.js ./

# Install production dependencies
RUN npm install -g pnpm
RUN pnpm install --prod

# Copy built assets and dependencies from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001 && \
    chown -R nextjs:nodejs /app

USER nextjs

# Expose port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Command to run the application
CMD ["node", "server.js"]
