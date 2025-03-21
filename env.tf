data "local_sensitive_file" "env" {
  filename = "${path.module}/.env"
}