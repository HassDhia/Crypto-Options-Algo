variable "project_id"        { type = string }
variable "region"            { type = string  default = "europe-west1" }
variable "gke_cluster_name"  { type = string  default = "crypto-edge-dev" }
variable "node_machine_type" { type = string  default = "e2-standard-4" }
