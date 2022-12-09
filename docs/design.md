# Design

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

## Solver?

We started using clingo with ASP (answer set programming) and @vsoch compared queries between the two.
The database always won by a LOT. Here is an example

```console
SELECT DISTINCT cloud, instance FROM instances WHERE value_number IS NOT NULL AND attribute='gpus' and value_number >= 4;
Clingo time: 0.5402274131774902 seconds
Manual time: 0.001077890396118164 seconds
```

The last version of the repo with the solver is [this commit](https://github.com/converged-computing/cloud-select/tree/67ecac0846f2e9a262305ef2f15134c1b423ab91)
if you are interested. It's since been gutted out.

## Previous Art

- AWS already has an instance selector in Go https://github.com/aws/amazon-ec2-instance-selector
- GCP has one in perl https://github.com/Cyclenerd/google-cloud-compute-machine-types

I think I'm still going to use Python for faster prototyping.

[home](/README.md#cloud-select)
