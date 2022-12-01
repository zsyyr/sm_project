FROM python:3.9

RUN mkdir /code

COPY ./requirements.txt /code/requirements.txt

# RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r /code/requirements.txt
RUN pip install -r /code/requirements.txt
RUN apt-get update
RUN apt-get install -y libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1

ENV PYTHONPATH "${PYTHONPATH}:/code/sm_crawler"
# ENV TZ Asia/Shanghai
ENV TZ Europe/Brussels
# WORKDIR /code

# CMD ["python","sm_crawler/crawler.py"] dock