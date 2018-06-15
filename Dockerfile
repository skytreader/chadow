FROM ubuntu:16.04

RUN apt-get update && apt-get install -y jq curl git python python3 python-setuptools unzip wget
RUN git clone --depth 1 https://github.com/sstephenson/bats.git && cd bats && ./install.sh /usr/local
RUN useradd -m -U -s /bin/bash chadow
USER chadow
RUN cd ~ && wget https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh && chmod +x virtualenv-burrito.sh && ./virtualenv-burrito.sh

COPY . ./chadow
WORKDIR ./chadow
ENTRYPOINT /bin/bash -c "source ~/.venvburrito/startup.sh && bats battests"
