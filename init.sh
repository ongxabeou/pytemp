#!/bin/bash
## Install
pip instal -r requirement

## Teardown and migrate database

py run.py teardown

## Run App port 5000

py app.py run &

## Run under background process

py run.py &