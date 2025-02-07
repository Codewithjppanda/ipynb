# Use an official Jupyter Notebook image with nbconvert
FROM jupyter/base-notebook

# Switch to root for system package installation
USER root

# Set the working directory
WORKDIR /app

# Add PATH environment variable
ENV PATH="/opt/conda/bin:$PATH"

# Install required packages and dependencies
RUN conda install -y flask flask-cors werkzeug jupyter nbconvert && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    pandoc \
    texlive-base \
    texlive-xetex \
    texlive-latex-recommended && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Create directories and set permissions
RUN mkdir -p /app/uploads /app/outputs && \
    chmod -R 777 /app/uploads /app/outputs && \
    chown -R jovyan:users /app

# Copy app files
COPY app.py .
COPY templates ./templates

# Ensure proper permissions for copied files
RUN chown -R jovyan:users /app

# Switch back to the non-root user
USER jovyan

# Expose the port
EXPOSE 5000

# Run the Flask app directly without shell
CMD ["python3", "-u", "app.py", "--host=0.0.0.0", "--port=5000"]
