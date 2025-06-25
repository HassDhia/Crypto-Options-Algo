terraform {
  backend "gcs" {
    bucket = "tfstate-crypto-options-algo"
    prefix = "gke/dev"
  }
}
