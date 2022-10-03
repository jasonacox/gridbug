FROM python:3.8-alpine
WORKDIR /app
RUN pip3 install influxdb
COPY gridbug.py gridbug.py
COPY gridbug.html gridbug.html
CMD ["python3", "gridbug.py"]
EXPOSE 8777