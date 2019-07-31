#!/bin/bash

watchexec -w ./ -s SIGINT -r "poetry run ./main.py"
