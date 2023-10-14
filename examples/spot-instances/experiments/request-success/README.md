# Request Success

For this prototype experiment we want to select a subset of instance types (based on a minimum cpu, gpu requirement, and lowest cost)
and assess our ability to get an allocation. I already am fairly confident that asking for 1 type is not a successful strategy, so for this experiment I want to:

1. Start with a base request up to 10 instances (arbitrary number)
2. Time how long it takes to get a managed node group for sizes 1..10.

If this works, we can figure out an optimal number to use when we ask, and then plug them into Flux to use.
The instances can be further filtered. At this point I'm interested in matching the architecture, GPU/no GPU, and minimum vCPU.

## Design

For this experiment we will:

1. Use [kubescaler](https://github.com/converged-computing/kubescaler) as a client to ask for managed node groups for an EKS cluster.
2. Use [cloud-select](https://github.com/converged-computing/cloud-select) (the repository here) to select a group of 10 instance types that support spot.
3. Make the request for the managed node group and time how long it takes (and cut at some point)
4. Do this procedure across a few groups and sizes within each group. This means randomly selecting from the 10, from 2 to 10. This is strategy that could be changed, but I think reasonable for a first try.
5. Record data and look at results!

I think (hope) I can create one cluster and then add/remove groups from it so I don't have to wait until I'm decomposed for the clusters to create.

## Experiments

For these first experiments I want to:

- Filter instances down to a set number of vCPU, meaning there is no variation
- Ask for up to 10 for each
- No GPU!
- The same architecture (x86_64)
- Always use price sorted from least to greatest (no risky randomize!)
- Time how long it takes to get each set of instances (a particular set of types and count)

I am going to do a constant count for now just to keep the matrix small (and this is testing anyway).
The above can be varied, of course, but this is the approach I think is sound to start with.
Take a look at help first:


```bash
python run-experiment.py --help
```

And then run (using defaults or your own settings)

```bash
python run-experiment.py
```

Here is a small (testing experiment) that I ran just to sanity check things working. The longest time you will wait is to create the cluster
and then create/delete nodegroups. Note that the number of experiments we will run is the range between the min spot request and the max instance types. In simpler terms, if you are allowing for a set of 10 spot instance types, we will test asking for a minimum value up to the (actual) max that is retrieved.

```bash
mkdir -p ./data

# The request below says:
#   Select from a max of 10 instance types (depends on filter criteria if you get that many)
#   Ask for spot instance counts between 3 and 6 (e.g., node groups of these sizes)
#   Always ask for 4 nodes
python run-experiment.py --outfile ./data/testing-tiny-result.json --cluster-name cluster-tiny --max-instance-types 10 --min-spot-request 3 --max-spot-request 6 --nodes 4
```

Note that vcpu (and experiment plans) are set in the experiments defined at the top of "run-experiment.py." This could be tweaked to be elsewhere! 
Also note that when you create multiple node groups, it will already have an auth config and print an error. You can ignore that :)

## TODO and questions

- We likely want to run some number of iterations. Should that go in the script or should (maybe better) we create clusters at different times to get them? I am just thinking if we are doing spot requests all at once, we are probably likely to be able to get the same nodes again, but maybe I'm wrong.
