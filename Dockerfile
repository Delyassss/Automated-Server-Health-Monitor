FROM debian:bookworm

RUN apt-get update  && apt-get install -y \ 
    python3 \
    python3-pip

COPY ./setup   /home/AserverHC

RUN chmod +x /home/AserverHC/setup/*.py

RUN pip3 install psutil

WORKDIR /home/AserverHC/setup/


ENTRYPOINT ["python3" , "script.py"]

