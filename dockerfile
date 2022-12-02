FROM python:3.9
ADD requirements.txt /
RUN pip install -r requirements.txt
RUN pip install kafka-python
ADD chistadata-connector.py /
CMD [ "python", "./chistadata-connector.py" ]

