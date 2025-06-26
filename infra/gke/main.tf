resource "google_compute_network" "vpc" {
  project                 = var.project_id
  name                    = "btc-options-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  project       = var.project_id
  name          = "btc-options-subnet"
  ip_cidr_range = "10.10.0.0/16"
  region        = var.region
  network       = google_compute_network.vpc.id

  secondary_ip_range {
    range_name    = "pods-range"
    ip_cidr_range = "10.20.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services-range"
    ip_cidr_range = "10.30.0.0/16"
  }
}

module "gke" {
  source  = "terraform-google-modules/kubernetes-engine/google//modules/private-cluster"
  version = "~> 30.0"

  project_id  = var.project_id
  name        = var.gke_cluster_name
  region      = var.region
  network     = google_compute_network.vpc.name
  subnetwork  = google_compute_subnetwork.subnet.name
  ip_range_pods = "pods-range"
  ip_range_services = "services-range"

  node_pools = [
    {
      name         = "primary"
      machine_type = "e2-standard-2"  # Reduced from e2-standard-4 to save CPU
      min_count    = 2                 # Reduced from 3
      max_count    = 2                 # Reduced from 3
      node_locations = "europe-west1-b"
    },
  ]

}

# ----------- OIDC SA for GitHub Actions -----------
resource "google_service_account" "gha_oidc" {
  project      = var.project_id
  account_id   = "gha-terraform"
  display_name = "GitHub Actions Terraform deployer"
}

resource "google_project_iam_member" "gha_oidc_token" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityUser"
  member  = "serviceAccount:${google_service_account.gha_oidc.email}"
}

output "gha_service_account_email" {
  value = google_service_account.gha_oidc.email
}
