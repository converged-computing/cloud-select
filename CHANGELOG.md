# CHANGELOG

This is a manually generated log to track changes to the repository for each release.
Each section should include general headers such as **Implemented enhancements**
and **Merged pull requests**. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)

The versions coincide with releases on pip. Only major versions will be released as tags on Github.

## [0.0.x](https://github.com/converged-computing/cloud-select/tree/main) (0.0.x)
 - support for parsing Google prices and preemptible (spot) instances (0.0.25)
 - add support for since to aws spot prices (0.0.24)
 - support for aws spot prices (function to request) (0.0.23)
 - aws prices no longer works to receive an empty NextToken (0.0.22)
 - fix one-off error for table listing (0.0.21)
   - support for spot-instance example
 - add aws price cache example and use non-deprecated oras upload_* functions (0.0.2)
 - rename module to cloudselect (0.0.19)
 - bugfix for sorting by prices with select (0.0.18)
 - selector class (with interactive or automated select) (0.0.17)
 - support for `--efa` flag to find AWS instances that support it (0.0.16)
 - exponential backoff added for using aws products/prices api (0.0.15)
 - dbshell command added with tutorial, testing for queries and shell (0.0.14)
 - bugfix to allow oras without auth for pull (0.0.13)
   - addition of basic container tutorial
   - basic tests for settings (missing add)
 - bug fixes for unauthenticated google cloud (0.0.12)
 - support for cache clear, update, and push commands (0.0.11)
 - addition of docs and bug fixes for instance select (0.0.1)
 - initial skeleton release of project (0.0.0)
