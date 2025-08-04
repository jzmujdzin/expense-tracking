
provider "google" {
  project = var.project_id
  region  = var.location
}

resource "google_service_account" "service_account" {
  account_id                   = var.service_name
  display_name                 = "Expense Tracking Cloud Run Service Account"
  create_ignore_already_exists = true
}

resource "google_cloud_run_v2_service_iam_member" "invoker" {
  location = google_cloud_run_v2_service.expense_tracker.location
  name     = google_cloud_run_v2_service.expense_tracker.name
  project  = var.project_id
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "storage_object_creator" {
  project = var.project_id
  role    = "roles/storage.objectCreator"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.service_account.email}"
}


data "google_artifact_registry_docker_image" "default" {
  location      = var.location
  repository_id = var.repository_id
  image_name    = var.image_name
}

resource "google_project_service" "cloudrun" {
  service                    = "run.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = false
}

resource "google_project_service" "artifact_registry" {
  service                    = "artifactregistry.googleapis.com"
  disable_on_destroy         = false
  disable_dependent_services = false
}


resource "google_cloud_run_v2_service" "expense_tracker" {
  name     = var.service_name
  location = var.location

  template {
    service_account = google_service_account.service_account.email
    containers {
      image = data.google_artifact_registry_docker_image.default.self_link
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.location
      }
      env {
        name  = "GCS_BUCKET"
        value = var.bucket_name
      }
      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }
    }

  }
  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
  ingress = "INGRESS_TRAFFIC_ALL"

  depends_on = [
    google_project_service.cloudrun,
    google_project_service.artifact_registry
  ]
}


output "cloud_run_service_url" {
  description = "The URL of the deployed Cloud Run service."
  value       = google_cloud_run_v2_service.expense_tracker.uri
}