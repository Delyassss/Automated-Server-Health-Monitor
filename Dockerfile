FROM debian:bookworm

RUN apt-get update  && apt-get install -y \ 
     python3 \
    python3-pip \
    python3-dev \
    gcc \

COPY ./setup   /home/AserverHC/setup/

RUN pip3 install psutil

WORKDIR /home/AserverHC/setup/


ENTRYPOINT ["python3" , "script.py"]

