variable "project_id" {
	type = string
	description = "GCS Project ID"
}

variable "region" {
	type = string
	default = "europe-west3"
	description = "Region for GCP resources"
}

variable "registry_id" {
	type = string
	description = "Name of artifact registry repository"
}

// For resource 'run_service'
/*variable "image_id" {
	type = string
	default = "main-1"
	description = "Id of image pushed the artifact registry repository"
}

variable "google_api_key" {
	type = string
	default = "google_api_key"
	description = "API key for Google Generative AI"
}

variable "tavily_api_key" {
	type = string
	default = "tavily_api_key"
	description = "API key for Tavily Search Engine"
}

variable "co_api_key" {
	type = string
	default = "co_api_key"
	description = "API Key for Cohere Platform"
}*/