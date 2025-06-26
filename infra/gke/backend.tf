terraform {
  backend "gcs" {
    bucket = "btc-options-terraform-state"
    prefix = "gke/dev"
  }
}
