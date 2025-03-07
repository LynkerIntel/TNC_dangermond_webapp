# NGEN Model Dashboard - TNC Dangermond

A Dash-based web app to visualize NGEN model output for the Dangermond Preserve in Santa Barbara County, CA.

## Installation for Development

The app includes an Anaconda-based `environment.yml` as well as `requirements.txt`. The Anaconda environment is useful for local development, while the pip-based `requirements.txt` is included in the Docker image for deployment.


1. **Clone the repository:**
   ```bash
   git clone https://github.com/LynkerIntel/TNC_dangermond_webapp.git
   ```

2. **Create a Conda environment (or use any Python environment):**
   ```bash
   conda create --file environment.yml
   ```

3. **Activate the environment:**
   ```bash
   conda activate tnc_web_env
   ```

4. **Set up AWS credentials (if running locally):**
   - Ensure you have local AWS credentials with access to the `tnc_dangermond` bucket.
   - Edit your AWS credentials file:
     ```bash
     vi ~/.aws/credentials
     ```
   - If the app resources are hosted in a different bucket or an alternative cloud service, update `./data_loader.py` with the appropriate base directory or request method.

5. **Navigate to the project directory:**
   ```bash
   cd TNC_dangermond_webapp
   ```

6. **Run the application:**
   ```bash
   python application.py
   ```

## Deployment
The app is deployed for testing and development with a free render.com server, via Dockerhub image.

The container is built via `docker-compose.yml` which attaches secrets to the container via an `.env` and exposes port 10000. The `.env` should contain AWS credentials (or alternative data location) in order to access the S3 bucket. render.com uses `amd64` architecture, which is defined in the `Dockerfile`. 