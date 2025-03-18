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
The app is deployed for testing and development with a free `render` server instance, via Dockerhub image.

The container is built via `docker-compose.yml` which attaches secrets to the container via an `.env` and exposes port 10000. The `.env` should contain AWS credentials (or alternative data location) in order to access the S3 bucket. Note that render.com uses `amd64` architecture, which is defined in the `Dockerfile`. For deployment elsewhere, such as ECS, this should be updated to the proper platform.

The data required to run the app is a series of parquet files (and .csv). These are monthly aggregations (in the case of ngen model output) as well as a repackaging of groundwater data
from the dendra repository. The total storage size is only around ~15mb. The files are:
```
/tnc-dangermond/webapp_resources/cfe_20241103_troute_cat23.parquet
/tnc-dangermond/webapp_resources/cfe_routed_flow_monthly_af.parquet
/tnc-dangermond/webapp_resources/cfe_routed_flow_monthly_cfs.parquet
/tnc-dangermond/webapp_resources/flow_17593507_mean_estimated_1982_2023.csv
/tnc-dangermond/webapp_resources/gw_level_raw_hourly_feet.parquet
/tnc-dangermond/webapp_resources/ngen_validation_20241103_monthly.nc
```