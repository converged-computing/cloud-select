# Spot Instances

The goal here is to group AWS instances into resources ranges that satisfy a minimum criteria.
Since instance types are fairly consistent, we would only need to run this incrementally to generate updated
data for some new set. Then we can:

1. use the set in a spot request to assess our ability to get the allocation
2. plug into the flux operator to dynamically create the cluster based on the spec!

See [experiments](experiments) for doing this. The assets here are used to generate data and listing
of instances to test.


## Usage

First, generate the data [instances-aws.csv](instances-aws.csv).

```bash
python spot-instances.py gen

# Don't use a cache
python spot-instances.py gen --no-cache
```

Next, filter to your selection! Look at the usage first (`python spot-instances.py select --help`) to see options. Minimally you should choose:

 - min-vcpu (2 vCPU == 1 CPU)
 - max-vcpu

And the arch defaults to x86_64. Here are some examples that get me a relatively small set. This asks for a set of 5:

```bash
# Default is to use the cache, 2 or fewer threads per core, no GPU, us-east-1
$ python spot-instances.py select --min-vcpu 32 --max-vcpu 32 --number 5
```
```console
Selected subset table:
         instance  bare_metal    arch  vcpu  threads_per_core  memory_mb    gpu    price
333  r6in.8xlarge       False  x86_64    32                 2     262144  False  1.47200
592   c7i.8xlarge       False  x86_64    32                 2      65536  False  1.47200
483  c5ad.8xlarge       False  x86_64    32                 2      65536  False  1.54100
159   m6a.8xlarge       False  x86_64    32                 2     131072  False  1.64564
727  c6id.8xlarge       False  x86_64    32                 2      65536  False  1.66880

😸️ Final selection of spot:
r6in.8xlarge
c7i.8xlarge
c5ad.8xlarge
m6a.8xlarge
c6id.8xlarge

🤓️ Mean (std) of price
$1.56 ($0.09)
```

Note that by default we sort by price and select the lowest, and show the mean and standard deviation at he end.
Try setting a max price instead:

```bash
$ python spot-instances.py select --min-vcpu 32 --max-vcpu 32 --max-price 3
```
```console
Selected subset table:
         instance  bare_metal    arch  vcpu  threads_per_core  memory_mb    gpu    price
333  r6in.8xlarge       False  x86_64    32                 2     262144  False  1.47200
592   c7i.8xlarge       False  x86_64    32                 2      65536  False  1.47200
483  c5ad.8xlarge       False  x86_64    32                 2      65536  False  1.54100
159   m6a.8xlarge       False  x86_64    32                 2     131072  False  1.64564
727  c6id.8xlarge       False  x86_64    32                 2      65536  False  1.66880
636   c6a.8xlarge       False  x86_64    32                 2      65536  False  1.76480
351  m5ad.8xlarge       False  x86_64    32                 2     131072  False  1.80300
513    h1.8xlarge       False  x86_64    32                 2     131072  False  1.87200
90   inf2.8xlarge       False  x86_64    32                 2     131072  False  1.96786
416   r5a.8xlarge       False  x86_64    32                 2     262144  False  1.97200
735  c6in.8xlarge       False  x86_64    32                 2      65536  False  1.99584
337   m5n.8xlarge       False  x86_64    32                 2     131072  False  2.06900
267  r5ad.8xlarge       False  x86_64    32                 2     262144  False  2.09600
65   m5dn.8xlarge       False  x86_64    32                 2     131072  False  2.34100
172    r4.8xlarge       False  x86_64    32                 2     249856  False  2.34100
341  r6id.8xlarge       False  x86_64    32                 2     262144  False  2.54920
472   i4i.8xlarge       False  x86_64    32                 2     262144  False  2.74600
330    i3.8xlarge       False  x86_64    32                 2     249856  False  2.87600

😸️ Final selection of spot:
r6in.8xlarge
c7i.8xlarge
c5ad.8xlarge
m6a.8xlarge
c6id.8xlarge
c6a.8xlarge
m5ad.8xlarge
h1.8xlarge
inf2.8xlarge
r5a.8xlarge
c6in.8xlarge
m5n.8xlarge
r5ad.8xlarge
m5dn.8xlarge
r4.8xlarge
r6id.8xlarge
i4i.8xlarge
i3.8xlarge

🤓️ Mean (std) of price
$2.01 ($0.42)
```

Also try adding `--randomize` so it randomizes the set first (before filtering down to price, for example)

```bash
$ python spot-instances.py select --min-vcpu 32 --max-vcpu 32 --number 5 --randomize
```
```console
Selected subset table:
         instance  bare_metal    arch  vcpu  threads_per_core  memory_mb    gpu     price
174   m7i.8xlarge       False  x86_64    32                 2     131072  False   5.61408
624    r5.8xlarge       False  x86_64    32                 2     262144  False  14.30200
735  c6in.8xlarge       False  x86_64    32                 2      65536  False   1.99584
159   m6a.8xlarge       False  x86_64    32                 2     131072  False   1.64564
116    d3.8xlarge       False  x86_64    32                 2     262144  False   4.93587

😸️ Final selection of spot:
m7i.8xlarge
r5.8xlarge
c6in.8xlarge
m6a.8xlarge
d3.8xlarge

🤓️ Mean (std) of price
$5.7 ($5.12)
```

Use that with caution since it will select from the higher priced instances!
Note that we may need more filters for the above! This is a testing script right now.
