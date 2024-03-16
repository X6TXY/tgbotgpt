FROM python:3.11

# Set environment variables
ENV NIXPACKS_PATH /opt/venv/bin:$NIXPACKS_PATH

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --upgrade pip && \
    python -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -r requirements.txt

# Copy your application code
COPY . /app

# Set the command to run your app
CMD ["python", "main.py"]
