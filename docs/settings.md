# Settings

Cloud select supports a settings.yml file, or a configuration file where
you can define settings and defaults. If you do nothing, the defaults
settings.yml is found within the cloud_select install directory, and you
can see it on GitHub [here](https://github.com/converged-computing/cloud-select/blob/main/cloud_select/settings.yml).
If you want to customize this file, it's recommended to create one in your
user home:

```bash
$ cloud-select config inituser
```
```console
Created user settings file /home/dinosaur/.cloud-select/settings.yml
```

You can then edit the file manually, or with edit:

```bash
$ cloud-select config edit
```

Or provide a config value "one off" for a command.

```bash
$ cloud-select instance -c set:cache_only:true ...
```

## Global Settings

The following settings are available. Note that this "global" set
is defined at the top level of the yaml, and indentened grouped sections
are described following it.

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| clouds | a list of cloud identifiers | true | `[aws, google]` |
| config_editor | the editor to use with `cloud-select config edit` | true | vim |
| cache_only | only retrieve data via cache and don't attempt to refresh it | true | false |
| disable_prices | disable adding prices | true | false |
| google | group of settings specific to google cloud | true | see below  |
| aws | group of settings specific to aws | true | see below  |
| instances | default filter settings for the instance command | false | see below  |


Note that the library is early in development and the settings and defaults
are subject (and likely) to change!

## Cloud Settings

### Google Cloud

In the `settings.yml` this group is under "google", e.g.,

```yaml
google:
  regions: ["us-east1", "us-west1", "us-central1"]
```

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| regions | a list of default Google Cloud Regions | true | `["us-east1", "us-west1", "us-central1"]` |



### Amazon Web Services

In the `settings.yml` this group is under "aws", e.g.,

```yaml
aws:
  regions: ["us-east-1"]
```

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| regions | a list of default AWS Regions | true | `["us-east-1"]` |


## Instance Settings

The most up-to-date representation of these settings is in the [cloud_select/main/schemas.py](https://github.com/converged-computing/cloud-select/blob/main/cloud_select/main/schemas.py) file.
and are all accessible on the command line (see `cloud-select instance --help`). In the `settings.yml` these settings are all under "instances" (and optional) e.g.,:

```yaml
instances:
  gpus: 1
```

You would want to set something here that you want as a default, always. Otherwise it's better to request attributes for your
select on the fly, on the command line.

**none of the fields here are required**


| Name | Type | Description | Default |
|------|------|-------------|---------|
| gpus | number | Number of gpus needed (assumes gpu-enabled wanted) and sets gpu min and max to the same value. |  unset |
| gpus-min | number | Min of total number of GPUs (e.g., 4) if --gpus-max not set, is infinity | unset |
| gpus-max | number | Max of total number of GPUs (e.g., 4) if --gpus-min not set, it is 0 | unset |
| gpu | boolean | GPU-enabled instance type | unset |
| gpu-memory | number | Total memory across GPUs in GiB (e.g., 4) sets --gpu-memory-min and --gpu-memory-max to the same value | unset |
| gpu-memory-min | number | Min of total memory across GPUs in GiB (e.g., 4 GiB) if --gpu-memory-max not set, is infinity | unset |
| gpu-memory-max| number | Max of total memory across GPUs in GiB (e.g., 4 GiB) if --gpu-memory-min not set, it is 0 | unset |
| gpu-model| string | GPU model name | unset |
| region |string | Regular expression or string to search for in region name. | unset |
| hypervisor | string | Hypervisor. | unset, can be one of "xen" or "nitro" | unset |
| memory | number | Total memory needed and sets memory min and max to the same value. | unset |
| memory-min | number | Min memory needed in GiB. if max not set, is infinity | unset |
| memory-max | number | Max memory needed in GiB if min not set, it is 0 | unset |
| instance-storage | number | Amount of local instance storage in GiB. Sets --instance-storage-min and -max to the same value. | unset|
| instance-storage-min| number | Minimum amount of local instance storage in GiB. If --instance-storage-max not set, is infinity. | unset |
| instance-storage-max | number | Maximum amount of local instance storage in GiB. If --instance-storage-min not set, is 0. | unset |
| cpus |number |Number of vcpus available to the instance type. Sets min and -max to the same value. | unset |
| cpus-min | number | Minimum number of vcpus available to the instance type. If max not set, is infinity. | unset |
| cpus-max | number | Maximum number of vcpus available to the instance type. If min not set, is 0. | unset |
| price-per-hour | number | Price/hour in dollars (e.g., 0.09) (sets min and max to the same value) | unset |
| price-per-hour-min | number | Minimum price/hour in dollars. If max not set, is infinity. | unset |
| price-per-hour-max | number |Maximum price/hour in dollars. If min not set, is 0." | unset |
| free-tier | boolean | Instance Types that support IPv6 | unset |
| cpu-arch | string | architecture of the CPU | unset, can be one of "x86_64/amd64", "x86_64_mac", "i386", "arm64" |
| cpu-vendor | string | manufacturer of CPU | unset can be one of "amd", "intel", "aws" |
| gpu-vendor | string | Vendor of the GPU | unset can be one of nvidia |
| disk-type | string | type of disk, hard disk or solid state | unset  can be one of "hdd", "ssd" |
| exclude-list | array | instance types which should be excluded w/ regex syntax (Example: `m[1-2]\.*)` | unset |
| include-list | array | instance types which should be included w/ regex syntax (Example: `m[1-2]\.*)` | unset |

Note that many of these have yet to be implemented as instance filters.

[home](/README.md#cloud-select)
