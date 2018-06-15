FROM ubuntu:16.04

RUN apt-get update && apt-get install -y jq curl git
RUN curl -sL https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh | $SHELL
RUN git clone --depth 1 https://github.com/sstephenson/bats.git && cd bats && ./install.sh /usr/local

COPY . ./chadow
WORKDIR ./chadow
