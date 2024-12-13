variable "opennebula_endpoint" {
  description = "Endpoint URL for OpenNebula RPC2 API"
  default     = "http://fe1.km.home:2633/RPC2"
}

variable "template_name" {
  description = "Name of the OpenNebula template"
  default     = "ubuntu_2204_noimage_tf"
}

variable "image_name" {
  description = "Name of the OpenNebula image"
  default     = "Base Ubuntu Server Image"
}

variable "frontend_net_name" {
  description = "Name of the frontend network"
  default     = "frontend_net"
}

variable "backend_net_name" {
  description = "Name of the backend network"
  default     = "backend_net"
}

variable "master_fe_ips" {
  description = "Frontend IP addresses for Kubernetes masters"
  default     = ["192.168.2.150", "192.168.2.151"]
}

variable "worker_fe_ips" {
  description = "Frontend IP addresses for Kubernetes workers"
  default     = ["192.168.2.160", "192.168.2.161"]
}

variable "master_be_ips" {
  description = "Backend IP addresses for Kubernetes masters"
  default     = ["192.168.100.1", "192.168.100.2"]
}

variable "worker_be_ips" {
  description = "Backend IP addresses for Kubernetes workers"
  default     = ["192.168.100.3", "192.168.100.4"]
}
