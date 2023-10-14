# Spot Instances

The goal here is to group AWS instances into resources ranges that satisfy a minimum criteria.
Since instance types are fairly consistent, we would only need to run this incrementally to generate updated
data for some new set. Then we can:

1. use the set in a spot request to assess our ability to get the allocation
2. plug into the flux operator to dynamically create the cluster based on the spec!

## Usage

First, generate the data [instances-aws.csv](instances-aws.csv)

```
python spot-instances.py gen 
```

Next, filter to your selection! Look at the usage first (`python spot-instances.py select --help`) to see options. Minimally you should choose:

 - min-vcpu (2 vCPU == 1 CPU)
 - max-vcpu

And the arch defaults to x86_64. Here are some examples that get me a relatively small set:

```bash
python spot-instances.py select --min-vcpu 32 --max-vcpu 48 --max-threads-per-core 1

# This gets more, but ask for 10 (lowest price 10)
python spot-instances.py select --min-vcpu 32 --max-vcpu 48 --number 10
```

Note that we may need more filters for the above! This is a testing script right now.
