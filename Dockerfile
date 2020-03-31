FROM alpine:3.11

# Do stuff that's rarely needed
RUN echo UTC >/etc/timezone
RUN apk --no-cache add python3 python3-dev git zip alpine-sdk libffi-dev libressl-dev musl-dev && \
    python3 -m ensurepip && \
    pip3 install --upgrade pip && \
    mkdir /rli

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN pip3 install poetry

COPY pyproject.toml poetry.lock /rli/
RUN cd /rli && poetry export -f requirements.txt -o requirements.txt
RUN cd /rli && pip3 install -Ur requirements.txt

# Add source code
COPY . /rli
COPY entrypoint.sh /entrypoint.sh

RUN cd /rli && \
    pip install -e .

WORKDIR /rli
ENTRYPOINT ["/entrypoint.sh"]
