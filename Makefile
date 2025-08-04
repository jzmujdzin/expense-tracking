GCP_PROJECT ?= $(shell gcloud config get-value project)
GCP_LOCATION ?= europe-west1
GCP_BUCKET ?= expense-tracking
PORT ?= 8080
ARTIFACT_REGISTRY_URI ?= ${GCP_LOCATION}-docker.pkg.dev/${GCP_PROJECT}/expense-tracking

build:
	@docker build . -t exp_agent

run: build
	@docker run --rm \
	--name exp_agent \
	-p ${PORT}:${PORT} \
	-e PORT=${PORT} \
	-e GOOGLE_GENAI_USE_VERTEXAI=TRUE \
	-e GOOGLE_CLOUD_PROJECT=${GCP_PROJECT} \
	-e GOOGLE_CLOUD_LOCATION=${GCP_LOCATION} \
	-e GCS_BUCKET=${GCP_BUCKET} \
	-v $(HOME)/.config/gcloud/application_default_credentials.json:/home/myuser/.config/gcloud/application_default_credentials.json \
	exp_agent

push: build
	@docker tag exp_agent ${ARTIFACT_REGISTRY_URI}/exp_agent:latest
	@docker push ${ARTIFACT_REGISTRY_URI}/exp_agent:latest

stop:
	@docker stop exp_agent || true

lint:
	@uv run ruff check --fix