# base image
FROM python:3.10-slim

# Install GDAL and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gdal-bin libgdal-dev libpq-dev build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Install dependencies
COPY requirements.txt /app


# use venv due to pep 688 enforcing environment use
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install dependencies:
RUN pip install -i https://m.devpi.net/jaraco/dev suds-jurko
RUN pip install -r requirements.txt


# environment variables for static assets and templates
ENV STATIC_FOLDER=static
ENV TEMPLATES_FOLDER=templates
ENV COMPRESSOR_DEBUG=COMPRESSOR_DEBUG
ENV DOCKER_BUILDKIT=0
ENV DASH_PROD=True

ADD "https://www.random.org/cgi-bin/randbyte?nbytes=10&format=h" skipcache

# copy files
COPY application.py /app
COPY data_loader.py /app
# COPY config.py /app



COPY assets /app/assets
COPY figures /app/figures
COPY layouts /app/layouts
COPY pages /app/pages

# Expose port
EXPOSE 10000

# Run application
CMD ["python3", "application.py"]
