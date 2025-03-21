terraform {
    required_version = ">=1.5"
    backend "local" {}
    required_providers {
        google = {
            source = "hashicorp/google"
        }
    }
}

provider "google" {
    project = var.project_id
    region = var.region
    credentials = file("./google_key.json")
}

# Artifact registry for containers
resource "google_artifact_registry_repository" "deploy-api-container-registry" {
  location      = var.region
  repository_id = var.registry_id
  format        = "DOCKER"
}

/*resource "google_cloud_run_service" "run_service" {
  name     = "run-service"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.registry_id}/${var.image_id}:latest"

        env {
          name  = "GOOGLE_API_KEY"
          value = var.google_api_key
        }
        env {
          name  = "TAVILY_API_KEY"
          value = var.tavily_api_key
        }
		env {
          name  = "CO_API_KEY"
          value = var.co_api_key
        }
      }
    }
  }
}*/


variable "gcp_service_list" {
  description ="The list of apis necessary for the project"
  type = list(string)
  default = [
    "cloudresourcemanager.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project = var.project_id
  service = each.key
}
