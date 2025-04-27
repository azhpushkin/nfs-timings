#!/bin/bash

echo "NFS Timings Svelte Frontend"
echo "=========================="
echo ""

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

# Try to run with npm, but provide fallback instructions if it fails
echo "Attempting to install dependencies and start the development server..."
echo ""

# Create a function to display manual instructions
show_manual_instructions() {
    echo ""
    echo "It seems there might be an issue with Node.js dependencies."
    echo ""
    echo "You can try running the following commands manually:"
    echo ""
    echo "To install dependencies:"
    echo "  npm install"
    echo ""
    echo "To start the development server:"
    echo "  npm run dev"
    echo ""
    echo "If you're experiencing issues with ICU library dependencies on macOS,"
    echo "you might need to reinstall or update Node.js using Homebrew:"
    echo "  brew reinstall node"
    echo "  brew link --overwrite node"
    echo ""
    echo "Alternatively, you can use a different Node.js version manager like nvm:"
    echo "  nvm install 16"
    echo "  nvm use 16"
    echo ""
}

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    if ! npm install; then
        echo "Failed to install dependencies."
        show_manual_instructions
        exit 1
    fi
fi

# Run the development server
echo "Starting development server..."
if ! npm run dev; then
    echo "Failed to start development server."
    show_manual_instructions
    exit 1
fi
