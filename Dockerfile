# Using the official python 3.7 docker image provided
FROM python:3.7

# Setting up the PYTHONUNBUFFERED env variable
ENV PYTHONUNBUFFERED 1

# ADD REQUIREMENTS AND ENV FILES TO WORKING DIR AND PREPARE FOR INSTALLATION
RUN mkdir /src
WORKDIR /src

COPY requirements.txt /src
RUN pip install -r requirements.txt 

COPY . /src
RUN ./test_script.sh

# EXPOSE THE PORT TO USE
EXPOSE 8000 
EXPOSE 5432
# RUN THE TESTS
CMD ["python", "manage.py", "test"]
