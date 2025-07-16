FROM ubuntu:latest
LABEL authors="jzmuj"

ENTRYPOINT ["top", "-b"]