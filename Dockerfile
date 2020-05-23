FROM ubuntu:16.04

RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && \ 
    apt-get update && apt-get install -y \
    jq \
    git \
    python3.7 \
    python-setuptools \
    # Needed by virtualenv-burrito!
    wget \
    curl \
    unzip \
    # End stuff needed by virtualenv-burrito
    sudo
RUN mkdir /opt/bin
RUN git clone --depth 1 https://github.com/sstephenson/bats.git && cd bats && ./install.sh /usr/local
RUN useradd -m -U -s /bin/bash chadow && \
    usermod -a -G root chadow && \
    chmod 775 -R /opt/bin && \
    chown chadow:chadow /media
USER chadow
RUN cd ~ && wget https://raw.githubusercontent.com/skytreader/virtualenv-burrito/master/virtualenv-burrito.sh && chmod +x virtualenv-burrito.sh && ./virtualenv-burrito.sh

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PATH="${PATH}:/opt/bin"
ENV FULL_TESTING=1
WORKDIR /home/chadow/chadow
ENTRYPOINT /bin/bash -c "source ~/.venvburrito/startup.sh && bats battests"
