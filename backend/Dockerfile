# Use the official Golang image to create a build artifact.
# This is known as a multi-stage build.
FROM golang:1.21-alpine as builder

# Set the Current Working Directory inside the container
WORKDIR /app

# Copy the go.mod file and download dependencies
COPY go.mod ./
RUN go mod tidy

# Copy the rest of the source code
COPY . .

# Build the Go app
# -o main: output file name
# ./cmd/server: the directory of the main package
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main ./cmd/server

# Start a new stage from scratch for a smaller image
FROM alpine:3.19

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy the Pre-built binary file from the previous stage
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main .

# Set ownership to the new user
RUN chown -R appuser:appgroup /app

# Switch to the non-root user
USER appuser

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run the executable
CMD ["./main"]
