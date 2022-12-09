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

🚧️ **under developemnt** 🚧️

This tool is under development and is not ready for production use.




## TODO and Questions

See our current [design document](https://github.com/converged-computing/cloud-select/blob/main/docs/design.md) for background about design.

- [ ]create cache of instance types and maybe prices in GitHub (e.g., automated update)
- [ ] add tests and testing workflow
  - [ ] properties testing for handling min/max/numbers
  - [ ] ensure that required set of attributes for each instance are returned (e.g., name, cpu, memory)
- [ ] how to handle instances that don't have an attribute of interest? Should we unselect them?
- [ ] add GPU memory - available in AWS and I cannot find for GCP
- [ ] should cache be organized by region to allow easier filter (data for AWS doesn't have that attribute)
- [ ] need to do something with costs
- [ ] can we just scrape prices from? https://cloud.google.com/compute/all-pricing
- [ ] TODO: we don't currently account for region as unique property in results (and need to)
- [ ] go through list of instance features and implement remaining (if possible)

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
