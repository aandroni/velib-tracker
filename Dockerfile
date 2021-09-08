# Start from minimal Python image to minimize final image size
FROM python:3.8-slim
LABEL maintainer="Alessio Andronico"

# API URL is passed when building the image
ARG API_URL
ENV API_URL=$API_URL

# Copy all files
COPY . /app
WORKDIR /app

# Install requirements
RUN pip install -r requirements.txt

# Run on container start
CMD [ "python", "viz-app/app.py" ]