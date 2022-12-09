# Cloud Select

This is a tool that helps a user select a cloud. It will make it easy for an HPC user to say:

> I need 4 nodes with these criteria, to run in the cloud.

And then be given a set of options and prices for different clouds to choose from.
There are some supporting packages that exist already (in Go for AWS) so we will
start there.

## Who is this intended for?

Cloud select is intended to help you do a quick comparison of resources
across clouds. It is agnostic to the cloud that you use, and will not give you
a direct suggestion of any particular cloud.

## Getting Started

### Installation

You can typically create an environment

```bash
$ python -m venv env
$ source env/bin/activate
```

and then pip install. You can install with no clouds (assuming you have a cache),
or support for all clouds, or selected clouds:

```bash
# No clouds (assuming using cache)
$ pip install cloud-select-tool

# All clouds
$ pip install cloud-select-tool[all]

# Google Cloud
$ pip install cloud-select-tool[google]

# Amazon web services
$ pip install cloud-select-tool[aws]
```

or install from the repository:

```bash
$ git clone https://github.com/converged-computing/cloud-select
$ cd cloud-select
$ pip install .
```

To do a development install (from your local tree):

```bash
$ pip install -e .
```

This should place an executable, `cloud-select` in your path.

### Clouds Supported

We currently support Amazon Web Services and Google Cloud. If you have cached data for either cloud,
that can be used without credentials. If not, credentials are required for an initial retrieval of data.
You can read about configuration and other details for each cloud [here](clouds.md).

## Commands

Read more about the commands shown above [here](commands.md#commands). For the
Python API, see [here](https://converged-computing.github.io/cloud-select/api/).
