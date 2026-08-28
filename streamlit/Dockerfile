# 1. Base Image: Using slim version to minimize size and ensure reproducibility
FROM python:3.12-slim AS base

# 2. Environment Variables: Prevent Python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# 3. Set working directory 
WORKDIR /app

# 4. Security: Create a non-privileged user 
RUN useradd --create-home appuser && chown -R appuser:appuser /app

# 5. Dependency Layer: Copy requirements first 
COPY --chown=appuser:appuser requirements.txt .

# Switch to the non-root user before running anything 
USER appuser

# Install dependencies into the user's home directory 
RUN pip install --no-cache-dir --user -r requirements.txt

# 6. Application: Copy the rest of the local source code 
COPY --chown=appuser:appuser . .

# 7. Network Configuration: 
EXPOSE 8501

# 8. Execution Command: Define the default command to execute your application
CMD ["streamlit", "run", "agent.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]

