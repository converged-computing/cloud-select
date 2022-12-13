# Cloud Select

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[![PyPI](https://img.shields.io/pypi/v/cloud-select-tool)](https://pypi.org/project/cloud-select-tool/)

<a target="_blank" rel="noopener noreferrer" href="https://github.com/converged-computing/cloud-select/blob/main/docs/assets/img/logo-transparent.png">
    <img align="right" style="width: 250px; float: right; padding-left: 20px;" src="https://github.com/converged-computing/cloud-select/raw/main/docs/assets/img/logo-transparent.png" alt="Cloud Select Logo">
</a>

This is a tool that helps a user select a cloud. It will make it easy for an HPC user to say:

> I need 4 nodes with these criteria, to run in the cloud.

And then be given a set of options and prices for different clouds to choose from.
There are some supporting packages that exist already (in Go for AWS) so we will
start there.

🚧️ **under development** 🚧️

This tool is under development and is not ready for production use. See our

 - ⭐️ [Documentation](https://converged-computing.github.io/cloud-select/) ⭐️
 - 📦️ [Pypi Package](https://pypi.org/project/cloud-select-tool/) 📦️

## TODO and Questions

- [ ] should cache be organized by region to allow easier filter (data for AWS doesn't have that attribute)
- [ ] go through list of instance features and implement remaining for Google (if possible)

### Future desires

These are either "nice to have" or small details we can improve upon. Aka, not top priority.

- should we allow currency outside USD? Probably not for now.
- could eventually support different resource types (beyond compute or types of prices, e.g., pre-emptible vs. on demand)
- aws instance listing (based on regions) should validate regions - an invalid regions simply returns no results

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
