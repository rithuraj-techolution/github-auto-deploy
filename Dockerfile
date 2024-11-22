FROM --platform=linux/amd64 python:3.9-slim

ARG PROJECT_ID=sylvan-dev
ARG ENV=default

ENV PYTHONUNBUFFERED=1
ENV ENV=${ENV}
ENV PROJECT_ID=${PROJECT_ID}

RUN apt-get update

RUN apt-get install -y software-properties-common lsb-release
RUN echo "deb [trusted=yes] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
RUN apt-get update
RUN apt-get install -y gh
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs npm

RUN apt-get install -y git
RUN pip install --upgrade pip

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

EXPOSE 5005

CMD ["python", "run.py"]
