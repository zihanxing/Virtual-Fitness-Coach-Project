# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Download the necessary data file
RUN wget https://huggingface.co/Mozilla/Mistral-7B-Instruct-v0.2-llamafile/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.llamafile

# Expose the port the app runs on
EXPOSE 8080

# Run the LLM service in the background
CMD ./mistral-7b-instruct-v0.2.Q4_K_M.llamafile --server --nobrowser --embedding --port 8080 &

# Run the Streamlit UI
CMD streamlit run main_page.py --server.port 8501 --server.address 0.0.0.0
