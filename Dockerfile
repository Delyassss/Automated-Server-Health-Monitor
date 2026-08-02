FROM debian:bookworm

RUN apt-get update && apt-get install -y \ 
    python3 \
    python3-pip \
    python3-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*





COPY ./requirements.txt /requirements.txt
COPY ./setup   /home/AserverHC/setup/

RUN pip3 install --break-system-packages --no-cache -r requirements.txt
#--break... forces pip to ignore the safety check and install the package globally anyway.

WORKDIR /home/AserverHC


ENTRYPOINT ["python3" , "./setup/script.py"]

