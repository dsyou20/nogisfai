#!/bin/bash 

INTERVAL=3

#jupyter lab --notebook-dir=/home/jovyan --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=/ --NotebookApp.max_buffer_size=10000000000 &

cd /home/jovyan/bizlogic
/opt/conda/bin/python /home/jovyan/bizlogic/main.py &

while true; 
    do ps -ef; 
    sleep $INTERVAL; 
done
