# Spot Instances

The goal here is to group AWS instances into resources ranges that satisfy a minimum criteria.
Since instance types are fairly consistent, we would only need to run this incrementally to generate updated
data for some new set. Then we can:

1. use the set in a spot request to assess our ability to get the allocation
2. plug into the flux operator to dynamically create the cluster based on the spec!

## Usage

First, generate the data [instances-aws.csv](instances-aws.csv)

```bash
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
```console
Selected subset table:
          instance  bare_metal    arch  vcpu  threads_per_core  memory_mb     price
16    g4ad.8xlarge       False  x86_64    32                 2     131072   0.00000
44    inf2.8xlarge       False  x86_64    32                 2     131072   0.00000
45    r5ad.8xlarge       False  x86_64    32                 2     262144   0.00000
69      r4.8xlarge       False  x86_64    32                 2     249856   0.00000
149    m5d.8xlarge       False  x86_64    32                 2     131072   0.00000
..             ...         ...     ...   ...               ...        ...       ...
524  r7iz.12xlarge       False  x86_64    48                 2     393216  10.67040
553  m5ad.12xlarge       False  x86_64    48                 2     196608  20.47200
465   m7a.12xlarge       False  x86_64    48                 1     196608  20.78208
516   r6i.12xlarge       False  x86_64    48                 2     393216  21.15400
651  c5ad.12xlarge       False  x86_64    48                 2      98304  22.27200

[108 rows x 7 columns]

😸️ Final selection of spot:
g4ad.8xlarge
inf2.8xlarge
r5ad.8xlarge
r4.8xlarge
m5d.8xlarge
c6i.8xlarge
m5a.8xlarge
c6in.8xlarge
p2.8xlarge
c6a.8xlarge
```

Note that we may need more filters for the above! This is a testing script right now.
