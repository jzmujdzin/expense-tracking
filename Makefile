GCP_PROJECT ?= $(shell gcloud config get-value project)
GCP_LOCATION ?= europe-west1
PORT ?= 8080

build:
	@docker build . -t exp_agent

run: build
	@docker run --rm \
	-p ${PORT}:${PORT} \
	-e PORT=${PORT} \
	-e GOOGLE_GENAI_USE_VERTEXAI=TRUE \
	-e GOOGLE_CLOUD_PROJECT=${GCP_PROJECT} \
	-e GOOGLE_CLOUD_LOCATION=${GCP_LOCATION} \
	-v $(HOME)/.config/gcloud/application_default_credentials.json:/home/myuser/.config/gcloud/application_default_credentials.json \
	exp_agent

lint:
	@uv run ruff check