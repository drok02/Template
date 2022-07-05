# Terraform Template 변환

- ### 주요 기능

  #### Template을 통한 멀티클라우드 호환성

  > 테라폼으로 Cloudstack에 구성된 수십 대의 서버, DB, 네트워크 장비들을 몇 번의 클릭으로 Openstack에 배포가 가능하다.

- ### Openstack basic provider

  ```
  # Define required providers
  terraform {
  required_version = ">= 0.14.0"
    required_providers {
      openstack = {
        source  = "terraform-provider-openstack/openstack"
        version = "~> 1.35.0"
      }
    }
  }
  
  # Configure the OpenStack Provider
  provider "openstack" {
    user_name   = "admin"
    tenant_name = "admin"
    password    = "devstack"
    auth_url    = "http://192.168.56.102/identity/v3"
  }
  ```

- ### Cloudstack basic provider

  ```
  # Configure the CloudStack Provider
  provider "cloudstack" {
    api_url    = "${var.cloudstack_api_url}"
    api_key    = "${var.cloudstack_api_key}"
    secret_key = "${var.cloudstack_secret_key}"
  }
  
  # Create a web server
  resource "cloudstack_instance" "web" {
    # ...
  }
  ```



- ### 멀티 클라우드(Cloudstack, Openstack) 파라미터 비교

  - **R** : Required, **O**: Optional, **NP** : Not present

1. #### Create a Disk volume(볼륨 생성)

   |      Argument      |  Type  | Openstack | Cloudstack |
   | :----------------: | :----: | :-------: | :--------: |
   |        name        | String |     R     |     R      |
   | attach_mode/attach | String |     O     |     O      |
   | device / device_id | String |     O     |     O      |
   |   disk_offering    | String |    NP     |     R      |
   |        size        | String |     R     |     O      |
   | virtual_machine_id | String |     O     |     O      |
   |      project       | String |    NP     |     O      |
   |   region / zone    | String |     O     |     R      |
   |    snapshot_id     | String |     O     |     NP     |
   |      image_id      | String |     O     |     NP     |
   | availability_zone  | String |     O     |     NP     |

   - #### Openstack Template

     ```
     resource "openstack_blockstorage_volume_v3" "volume_1" {
       region      = "RegionOne"
       name        = "volume_1"
       size        = 3
     }
     ```

   - #### Cloudstack Template

     ```
     resource "cloudstack_disk" "volume_1" {
       name               = "volume_1"
       disk_offering      = "custom"
       size               = 3
       zone               = "zone-1"
     }
     ```

     

2. #### Create VM Instance(VM 생성)

   |                   Argument                   |  Type  | Openstack | Cloudstack |
   | :------------------------------------------: | :----: | :-------: | :--------: |
   |                     name                     | String |     R     |     R      |
   |     flavor_name(id) \| service_offering      | String |     R     |     R      |
   |            network \| network_id             | String |     O     |     O      |
   |                region \| zone                | String |     O     |     R      |
   |          image_name(id) \| template          | String |     R     |     R      |
   |             key_pair \| keypair              | String |     O     |     O      |
   | security_groups \| security_group_ids(names) | String |     O     |     O      |
   |                  user_date                   | String |     O     |     O      |
   |              availability_zone               | String |     O     |     NP     |
   |                     tags                     | String |     O     |     NP     |

   - #### Openstack Template

     ```
     resource "openstack_compute_instance_v2" "instance_1" {
       name            = "server-1"
       image_id        = "ad091b52-742f-469e-8f3c-fd81cadf0743"
       flavor_name       = "m1.small"
       network {
         name = "my_network"
       }
     }
     ```

   - #### Cloudstack Template

     ```
     resource "cloudstack_instance" "instance_1" {
       name             = "server-1"
       service_offering = "small"
       network_id       = "6eb22f91-7454-4107-89f4-36afcdf33021"
       template         = "CentOS 6.5"
       zone             = "zone-1"
     }
     ```

### 
