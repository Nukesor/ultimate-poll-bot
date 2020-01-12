#!/bin/bash

watchexec -w ./ -s SIGINT -r "poetry run python ./main.py"
