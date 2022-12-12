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

Or limit to one cloud (on the fly) note that you can always change this to a default
via the `settings.yml` in the install root. You can also create your own version
to tweak in your home via:

```bash
$ cloud-select config inituser
```
