FROM debian:bookworm

RUN apt-get update  && apt-get install -y \ 
     python3 \
    python3-pip \
    python3-dev \
    gcc

COPY ./setup   /home/AserverHC/setup/

RUN pip3 install --break-system-packages psutil

WORKDIR /home/AserverHC


ENTRYPOINT ["python3" , "./setup/script.py"]

