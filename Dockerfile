# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download the necessary data file with progress bar
# RUN wget --progress=dot:giga https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.llamafile

# Expose the port the app runs on
EXPOSE 8080
EXPOSE 8501

# Run the LLM service in the background
CMD ["sh", "-c", "./mistral-7b-instruct-v0.2.Q4_K_M.llamafile --server --nobrowser --embedding --port 8080 & streamlit run main_page.py --server.port 8501 --server.address 0.0.0.0"]
