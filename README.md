# Cloud Select

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->

<a target="_blank" rel="noopener noreferrer" href="https://github.com/converged-computing/cloud-select/blob/main/docs/assets/img/logo-transparent.png">
    <img align="right" style="width: 250px; float: right; padding-left: 20px;" src="https://github.com/converged-computing/cloud-select/raw/main/docs/assets/img/logo-transparent.png" alt="Cloud Select Logo">
</a>

This is a tool that helps a user select a cloud. It will make it easy for an HPC user to say:

> I need 4 nodes with these criteria, to run in the cloud.

And then be given a set of options and prices for different clouds to choose from.
There are some supporting packages that exist already (in Go for AWS) so we will
start there.

## Usage

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
$ pip install cloud-select

# All clouds
$ pip install cloud-select[all]

# Google Cloud
$ pip install cloud-select[google]

# Amazon web services
$ pip install cloud-select[aws]
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

#### Google Cloud

For Google Cloud, you can generally [provide your default credentials](https://cloud.google.com/docs/authentication/client-libraries)

```bash
$ gcloud auth application-default login
```

to be discovered by the client. **You will need to enable the billing and compute APIs.**

### Commands

#### Instance

Find an instance based on availability. The client will connect to the clouds that you have cached data for,
and also the clouds that you have credentials for. If you have neither credentials nor data, you'll get an error.
There are a lot of variables to select from, see:

```bash
$ cloud-select instance --help
```

Let's ask for an exact amount of memory (as opposed to a min and/or max). This will not print instance
atoms to the screen.

```bash
$ cloud-select instance --memory 4
```

If you want to see the atoms:

```bash
$ cloud-select --verbose instance --memory 4
```

Or write the atoms to file:

```bash
$ cloud-select instance --memory 4 --out atoms.lp
```

Ask for a specific cloud on the command line (note you can also ask via your settings.yml configuration file for a more permanent default):

```bash
$ cloud-select --cloud google instance --cpus-min 200 --cpus-max 400
```

## Design

We can follow the design of the [aws selector tool](https://github.com/aws/amazon-ec2-instance-selector).

## Details

It is non-trivial to find the correct instances, or more generally, do cost comparison across clouds. A tool that can intelligently map a resource request to a set of options, and then present the user with a set of options (or a tool) can alleviate this current challenge. Importantly, we don't want to provide one answer, as the tool needs to be agnostic and not suggest a specific cloud.

### Implementation Idea

The implementation needs three parts: 1. a database of contender machines that is automatically updated at some frequency, 2. a tool that can parse this database and select a subset based on a user criteria, and 3. a final mapping of each in that selection to a cost estimate (using live or active APIs).

1. Start with APIs that can list instance types. We likely want to filter down into different groups.
2. Think about how to do a mapping across clouds. Likely this means being able to generalize (e.g., describe based on memory, size, GPU or other features, etc)
3. Save metadata about instances given the above attributes.
4. Can we generate a solve to find an optimal instance?

As an example use case, we could create a simple web app (and underlying user interface) that allows to define a jobspec
Jobspec → filter to top options → price API.

> Why Python?

To start, I was thinking we should use Python APIs for quick prototyping

> Why use ASP / clingo and do a solve?

Given matching requests for amounts, this is probablhy overkill - we could have iterables over a range of options filter this very easily.
The honest answer is that I thought it would be more fun to try using ASP. We can always
remove it for a simpler solution, as it does go against my better jugment to add extra dependencies that aren't needed.
That said, if the solve becomes more complex, it could be cool to have it.


## Previous Art

- AWS already has an instance selector in Go https://github.com/aws/amazon-ec2-instance-selector
- GCP has one in perl https://github.com/Cyclenerd/google-cloud-compute-machine-types

I think I'm still going to use Python for faster prototyping.

## TODO and Questions

- Are we allowed to provide a cache of instance types (e.g., automated update in GitHub?)
- should be able to set custom instances per cloud - either directly for a cloud, or generic string to match (e.g., "east")
- some logic to standardize regions (e.g., "east")
- add tests and testing workflow
  - properties testing for handling min/max/numbers
- Add Docker build / automated builds
- ensure that required set of attributes for each instance are returned (e.g., name, cpu, memory)
- how to handle instances that don't have an attribute of interest? Should we unselect them?
- pretty branded documentation
- selection should have sorting ability
- should we allow currency outside USD? Probably not for now.
- aws instance listing (based on regions) should validate regions - an invalid regions simply returns no results
- could eventually support different resource types (beyond compute or types of prices, e.g., pre-emptible vs. on demand)
- add GPU memory - available in AWS not sure gcp
- add AWS description from metadata (similar to GCP)

Planning for minimizing cost:

```lp
% generate a bunch of candidate_instance() predicates for each instance type that matches the user request
candidate_instance(Cloud, Instance) :-
  cloud_instance_type(Cloud, Instance),
  instance_attr(Cloud, Instance, Name, Value) : requested_attr(Name, Value).

% Tell clingo to select exactly one (at least one and at most one) of them
1 { select(Cloud, Instance) : candidate_instance(Cloud, Instance) } 1.

% associate the cost from your input facts with every candidate instance
selected_instance_cost(Cloud, Instance, Cost) :-
  select(Cloud, Instance),
  instance_cost(Cloud, Instance, Cost).

% tell clingo to find the solution (the one select() it got to choose with minimal cost
#minimize { Cost,Cloud,Instance : selected_instance_cost(Cloud, Instance, Cost) }.cv
```

## 😁️ Contributors 😁️

We use the [all-contributors](https://github.com/all-contributors/all-contributors)
tool to generate a contributors graphic below.

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://vsoch.github.io"><img src="https://avatars.githubusercontent.com/u/814322?v=4?s=100" width="100px;" alt="Vanessasaurus"/><br /><sub><b>Vanessasaurus</b></sub></a><br /><a href="https://github.com/converged-computing/cloud-select/commits?author=vsoch" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## License

HPCIC DevTools is distributed under the terms of the MIT license.
All new contributions must be made under this license.

See [LICENSE](https://github.com/converged-computing/cloud-select/blob/main/LICENSE),
[COPYRIGHT](https://github.com/converged-computing/cloud-select/blob/main/COPYRIGHT), and
[NOTICE](https://github.com/converged-computing/cloud-select/blob/main/NOTICE) for details.

SPDX-License-Identifier: (MIT)

LLNL-CODE- 842614
