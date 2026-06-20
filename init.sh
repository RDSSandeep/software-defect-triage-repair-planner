#!/usr/bin/env bash
echo "Initializing project..."

npm install

echo "Running checks..."
npm run build || true

echo "Init complete"