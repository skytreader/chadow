FROM ubuntu:16.04

RUN apt-get update && apt-get install -y \
    jq \
    git \
    python \
    python3 \
    python-setuptools \
    unzip \
    wget \
    # Needed by virtualenv-burrito!
    curl \
    sudo \
    openjdk-8-jdk
RUN mkdir /opt/bin && \
    wget -P /opt/bin https://services.gradle.org/distributions/gradle-4.8.1-bin.zip && \
    unzip -d /opt/bin /opt/bin/gradle-4.8.1-bin.zip && \
    ln -s /opt/bin/gradle-4.8.1/bin/gradle /usr/bin/gradle
RUN git clone --depth 1 https://github.com/sstephenson/bats.git && cd bats && ./install.sh /usr/local
RUN useradd -m -U -s /bin/bash chadow && \
    usermod -a -G root chadow && \
    chmod 775 -R /opt/bin
USER chadow
RUN cd ~ && wget https://raw.githubusercontent.com/brainsik/virtualenv-burrito/master/virtualenv-burrito.sh && chmod +x virtualenv-burrito.sh && ./virtualenv-burrito.sh

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PATH="${PATH}:/opt/bin"
WORKDIR /home/chadow/chadow
ENTRYPOINT /bin/bash -c "echo $(pwd) && source ~/.venvburrito/startup.sh && bats battests"
