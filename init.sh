#!/bin/bash
# todo: use tmux in here?
python app.py migrate --teardown 1 && python app.py run -h 0.0.0.0

# todo: run underground process in here
python app.py job_process
