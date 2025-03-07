# NGEN Model Dashboard - TNC Dangermond

A Dash-based web app to visualize NGEN model output for the Dangermond Preserve in Santa Barbara County, CA.

## Installation for development

The app includes an Anaconda-based `environment.yml` as well as `requirements.txt`. The anaconda env is useful for local development or execution, while the pip-based `requirements.txt` is included in the Docker image for deployment.

1. clone the repo `git clone https://github.com/LynkerIntel/TNC_dangermond_webapp.git`
2. `conda create --file environment.yml` (or any python env)
3. `conda activate tnc_web_env` (or equivalent for env manager)
3. If runing locally, setup local AWS credentials with access to the `tnc_dangermond` bucket. i.e. `~./aws/credentials`
4. `cd TNC_dangermond_webapp`
5. `python application.py`


## Deployment
Currently test deployed with free render.com server, via Dockerhub image.

The container is built via `docker-compose.yml` which attaches secrets to the container via an `.env` and exposes port 10000. The `.env` should contain a mapbox API and AWS credentials in order to access the s3 bucket. render.com uses `amd64` architecture, which is defined in the `Dockerfile`. 