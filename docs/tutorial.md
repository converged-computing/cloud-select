# Tutorials

This is a set (will be a set) of tutorials to help you get started with cloud select!

## Docker Tutorial

The easiest way to jump in is with docker. We provide a [pre-built container](https://github.com/converged-computing/cloud-select/pkgs/container/cloud-select):

```bash
$ docker run -it ghcr.io/converged-computing/cloud-select
```

And note this will eventually have versioned releases.  Running the container
will put you in an environment where the latest version of cloud-select is
installed:

```bash
$ which cloud-select
```
```console
/opt/conda/bin/cloud-select
```

### Basic Queries

Then try asking to query instances, with no arguments. This first call will use our container nightly cache provided at
[ghcr.io/converged-computing/cloud-select](https://github.com/converged-computing/cloud-select-cache/pkgs/container/cloud-select-cache)
and download to your host at `~/.cloud-select/cache`. This by default will present 25 results in the order
returned by the database.

```console
# cloud-select instance
```

![img/cloud-select-instance.png](img/cloud-select-instance.png)

Try asking for more results:

```bash
$ cloud-select --max-results 100 instance
```

Or try filtering by price:

```bash
$ cloud-select instance --price-per-hour-min 1.0
```

And also sorting, of course, either default or ascending:

```bash
$ cloud-select instance --price-per-hour-min 1.0 --sort-by price
$ cloud-select instance --price-per-hour-min 1.0 --sort-by price --asc
```

![img/cloud-select-prices.png](img/cloud-select-prices.png)

Or limit to one cloud (on the fly):

```bash
$ cloud-select --cloud aws instance
```

Note that you can always change this to a default
via the `settings.yml` in the install root. You can also create your own version
to tweak in your home via:

```bash
$ cloud-select config inituser
$ cloud-select config edit # uses vim, haarhar
```

### Advanced Queries

There are two types of attribute queries - asking for a specific value verbatim,
or a range. Here is asking for an exact match:

```bash
$ cloud-select instance --memory 1024
```

Try adding `--debug` to see debug information (this works generally for any command) and for an
instance query it shows the database query!


```bash
$ cloud-select --debug instance --memory 1024
```

![img/cloud-select-debug.png](img/cloud-select-debug.png)

If you are curious, we create an in-memory database each time from the cache data
to do the queries. It might be faster to save it to the filesystem and
not have to re-create it, but I haven't added that yet.
Next, let's try a range query:

```bash
$ cloud-select --debug instance --memory-min 1024 --memory-max 8000
```

This might nbe a more realistic query you would do:

```bash
$ cloud-select --debug instance --memory-min 1024 --memory-max 8000 --sort-by price --asc
```

You can see all the attributes available for query with `cloud-select --help`. Note
that not all instances support all attributes. E.g.,:

```bash
$ cloud-select --debug instance --gpu-memory-min 8000
GoogleCloudInstance does not support getting information about range:gpu_memory. Set allow_missing_attributes in your settings.yml to 'true' to continue anyway.
```
In the above, Google Cloud doesn't have this information. So we need to explicitly say "that's OK"

```bash
$ cloud-select -c set:allow_missing_attributes:true --debug instance --gpu-memory-min 8000
```

The `-c` flag is a one off config setting - here we are saying to set that particular setting to true. The
result will return a table with only AWS (the query doesn't select any Google).


**Note** We are still working on the client, and we don't have tests for a lot of
functionality (yet) so it's use at your own risk! E.g., include and exlude list are not
working yet (and need to be refactored to be a part of the database query). We are thinking about
use cases and if you have ideas please [contribute them here](https://github.com/converged-computing/cloud-select/issues/14).
