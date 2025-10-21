name: CI

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Say hello
        run: echo "Hello Agent"
git add .
git commit -m "message automatique"
git push origin main

