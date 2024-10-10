FROM python:3.10.4

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /Auth_LDAP_code

COPY requirements.txt /Auth_LDAP_code/
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libldap2-dev \
    libsasl2-dev \
    nano
RUN pip install -r requirements.txt
COPY ./ /Auth_LDAP_code/