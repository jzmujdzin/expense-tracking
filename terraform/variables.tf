# variables.tf

variable "project_id" {
  description = "The ID of the Google Cloud project."
  type        = string
}

variable "location" {
  description = "The location where the Cloud Run service will be deployed."
  type        = string
  default     = "europe-west1"
}

variable "service_name" {
  description = "The name for the Cloud Run service."
  type        = string
  default     = "expense-tracking"
}

variable "repository_id" {
  description = "The ID of the Artifact Registry repository where the container image is stored."
  type        = string
  default     = "expense-tracking" # Adjust this to your repository name
}

variable "bucket_name" {
  description = "The name of the Google Cloud Storage bucket to use for storing data."
  type        = string
  default     = "expense-tracking" # Adjust this to your bucket name
}

variable "image_name" {
  description = "The name of the container image to deploy on Cloud Run."
  type        = string
}

variable "user_email" {
  description = "Your personal Google email address to grant invoker permissions to."
  type        = string
}
