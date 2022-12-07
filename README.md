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

#### Sorting

By default we sort results based on the order the solver produces them.
However, you can ask to sort your results by an attribute, e.g., here is memory:

```bash
$ cloud-select --sort-by memory instance
```

By default, when sort is enabled on an attribute we do descending, so the largest values
are at the top. You can ask to reverse that with `--asc` for ascending, meaning we sort
from least to greatest:

```bash
$ cloud-select --asc --sort-by memory instance
```

#### Max Results

You can always change the max results (which defaults to 25):

```bash
$ cloud-select --max-results 100 instance
```

We currently sort from greatest to least. Set max results to 0 to set no limit.

```bash
$ cloud-select --max-results 0 instance
```

Note that this argument comes before the instance command.

#### Regions

For regions, note that you have a default set in your settings.yml. E.g.,:

```yaml
google:
  regions: ["us-east1", "us-west1", "us-central1"]

aws:
  regions: ["us-east-1"]
```

These are used for API calls to retrieve a filtered set, but not to filter that set.
You should generally be more verbose in this set, as it will be the meta set we further
filter. When appropriate, "global" is also added to find resources across regions. For
a one-off region for a query:

```bash
$ cloud-select  instance  --region east
```

Since region names are non consistent across clouds, the above is just a regular expression.
This means that to change region:

- edit settings.yml to change the global set you use
- add `--region` to a particular query to filter (within the set above).

If you have a cache with older data (and different regions) you will want to clear it.
If we eventually store the cache by region this might be easier to manage,
however this isn't done yet to maintain simplicity of design.

**Note** We use regions and zones a bit generously - on a high level a region encompasses
many zones, and thus a specification of `regions` (as shown below) typically
indicates regions, but under the hood we might be filtering the specific zones.
A result might generally be labeled with "region" and include a zone name.

#### Cache Only

To set a global setting to only use the cache (and skip trying to authenticate)
you cat set `cache_only` in your settings.yml to true:

```yaml
cache_only: true
```
This will be the default when we are able to provide a remote cache,
as then you won't be required to have your own credential to use the
tool out of the box!


## TODO and Questions

See our current [design document](docs/design.md) for background about design.

- [ ]create cache of instance types and maybe prices in GitHub (e.g., automated update)
- [ ]add tests and testing workflow
  - [ ]properties testing for handling min/max/numbers
  - [ ] ensure that required set of attributes for each instance are returned (e.g., name, cpu, memory)
- [ ] Add Docker build / automated builds
- [ ] how to handle instances that don't have an attribute of interest? Should we unselect them?
- [ ] pretty branded documentation
- [ ] add GPU memory - available in AWS and I cannot find for GCP
- [ ] should cache be organized by region to allow easier filter (data for AWS doesn't have that attribute)
- [ ] need to do something with costs
- [ ] test performance of using solver vs. not

### Future desires

These are either "nice to have" or small details we can improve upon. Aka, not top priority.

- should we allow currency outside USD? Probably not for now.
- could eventually support different resource types (beyond compute or types of prices, e.g., pre-emptible vs. on demand)
- aws instance listing (based on regions) should validate regions - an invalid regions simply returns no results
- for AWS description, when appropriate convert to TB (like Google does)

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
