FROM debian:sid
RUN echo 'deb http://mirror.psu.ac.th/debian/ sid main contrib non-free non-free-firmware' > /etc/apt/sources.list
RUN echo 'deb http://mirror.kku.ac.th/debian/ sid main contrib non-free non-free-firmware' >> /etc/apt/sources.list

RUN apt-get update && apt-get upgrade -y

RUN apt install -y python3 python3-dev python3-pip python3-venv npm git locales cmake
RUN sed -i '/th_TH.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8 
# ENV LC_ALL en_US.UTF-8



RUN python3 -m venv /venv
ENV PYTHON=/venv/bin/python3
RUN $PYTHON -m pip install wheel poetry gunicorn

WORKDIR /app

ENV PIPEK_SETTINGS=/app/pipek-production.cfg

COPY /dev/dash/pipek/cmd /app/pipek/cmd
COPY /dev/dash/poetry.lock /dev/dash/pyproject.toml /app/

RUN . /venv/bin/activate \
	&& poetry config virtualenvs.create false \
	&& poetry install --no-interaction --only main

COPY /dev/dash/pipek/web/static/package.json /dev/dash/pipek/web/static/package-lock.json pipek/web/static/
RUN npm install --prefix pipek/web/static

COPY /dev/dash/ /app
