#!/bin/bash

# Ultra-simple entrypoint script
echo "=== Pet Shop Starting ==="
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Script permissions: $(ls -la /app/entrypoint-simple.sh)"

# Just start the app - skip everything else for now
echo "Starting application directly..."
exec "$@"
