# Cloudstack Provider
terraform {
  required_providers {
    cloudstack = {
      source = "orange-cloudfoundry/cloudstack"
      version = "0.4.0"
    }
    openstack = {
      source = "terraform-provider-openstack/openstack"
      version = "1.43.0"
    }
  }
}

provider "cloudstack" {
  api_url    = "http://164.125.70.26:8080/client/api"
  api_key    = "0OcHRmqlLKxseRjIRoqW2sBtpIbaDDvnUElpbZVedZIVoZ1F11fcKi1n1MDGNuDWDXxBnG6Ba-jMFqSpAi5Tfg"
  secret_key = "xtbZVaUeYuds-ke_lCyRh0pZSdKdzUNHufwJeSvynO6847jJpWEb_aODEvsuHZ10os--xVFRAl3jepBiA33BAA"
}

provider "openstack" {
  user_name   = "admin"
  tenant_name = "admin"
  password    = "0000"
  auth_url    = "http://164.125.70.22/identity/v3"
  region      = "RegionOne"

  endpoint_overrides = {
    "network" = "http://164.125.70.22:9696/v2.0/"
    "compute" = "http://164.125.70.22/compute/v2.1/"
    "volume" = "http://164.125.70.22/volume/v3/4b3afecefc7e4beaa1039d76e5e677d5/"
    "volumev2" = "http://164.125.70.22/volume/v2/4b3afecefc7e4beaa1039d76e5e677d5/"
    "volumev3" = "http://164.125.70.22/volume/v3/4b3afecefc7e4beaa1039d76e5e677d5/"
    "image" = "http://164.125.70.22/image/"
    "identity" = "http://164.125.70.22/identity/"
    "block storage" = "http://164.125.70.22/volume/v3/4b3afecefc7e4beaa1039d76e5e677d5/"	
  }
}

