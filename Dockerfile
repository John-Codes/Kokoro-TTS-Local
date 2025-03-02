# Use your provided base image as the starting point
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# Install system dependencies and Python 3.10
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.10 as the default interpreter
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1 \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Upgrade pip
RUN pip3 install --upgrade pip

# Install PyTorch 2.6.0 with CUDA 12.4 support
RUN pip3 install torch==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# Copy and install Python dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy all project files into /app
WORKDIR /app
COPY . /app

# Expose the port FastAPI will run on
EXPOSE 8000

# Use a non-root user in production (optional but recommended)
# RUN useradd -m appuser && chown -R appuser:appuser /app
# USER appuser

# Start the API using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
