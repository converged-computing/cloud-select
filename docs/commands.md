# Commands

The following commands are currently supported. You can also view [settings](settings.md)
that can set defaults.

## instance

Find an instance based on availability. The client will connect to the clouds that you have cached data for,
and also the clouds that you have credentials for. If you have neither credentials nor data, you'll get an error.
There are a lot of variables to select from, see:

```bash
$ cloud-select instance --help
```

Let's ask for an exact amount of memory (as opposed to a min and/or max). This will not print instance
atoms to the screen.

```bash
$ cloud-select instance --memory 4
```

Ask for a specific cloud on the command line (note you can also ask via your settings.yml configuration file for a more permanent default):

```bash
$ cloud-select --cloud google instance --cpus-min 200 --cpus-max 400
```

### Sorting

By default we sort results based on the order the solver produces them.
However, you can ask to sort your results by an attribute, e.g., here is memory:

```bash
$ cloud-select --sort-by memory instance
```

By default, when sort is enabled on an attribute we do descending, so the largest values
are at the top. You can ask to reverse that with `--asc` for ascending, meaning we sort
from least to greatest:

```bash
$ cloud-select --asc --sort-by memory instance
```

### Max Results

You can always change the max results (which defaults to 25):

```bash
$ cloud-select --max-results 100 instance
```

We currently sort from greatest to least. Set max results to 0 to set no limit.

```bash
$ cloud-select --max-results 0 instance
```

Note that this argument comes before the instance command.

### Regions

For regions, note that you have a default set in your settings.yml. E.g.,:

```yaml
google:
  regions: ["us-east1", "us-west1", "us-central1"]

aws:
  regions: ["us-east-1"]
```

These are used for API calls to retrieve a filtered set, but not to filter that set.
You should generally be more verbose in this set, as it will be the meta set we further
filter. When appropriate, "global" is also added to find resources across regions. For
a one-off region for a query:

```bash
$ cloud-select  instance  --region east
```

Since region names are non consistent across clouds, the above is just a regular expression.
This means that to change region:

- edit settings.yml to change the global set you use
- add `--region` to a particular query to filter (within the set above).

If you have a cache with older data (and different regions) you will want to clear it.
If we eventually store the cache by region this might be easier to manage,
however this isn't done yet to maintain simplicity of design.

**Note** We use regions and zones a bit generously - on a high level a region encompasses
many zones, and thus a specification of `regions` (as shown below) typically
indicates regions, but under the hood we might be filtering the specific zones.
A result might generally be labeled with "region" and include a zone name.

### Cache Only

To set a global setting to only use the cache (and skip trying to authenticate)
you cat set `cache_only` in your settings.yml to true:

```yaml
cache_only: true
```

This will be the default when we are able to provide a remote cache,
as then you won't be required to have your own credential to use the
tool out of the box!

### Debugging

To debug, you can add `--debug` to see the database query that is done:

```bash
$ cloud-select --debug instance
```

## config

If you want to edit a configuration value, you can either edit the [cloud_select/settings.yml](https://github.com/converged-computing/cloud-select/blob/main/cloud_select/settings.yml).
file directly, or you can use `cloud-select config`, which will accept:

 - set to set a parameter and value
 - get to get a parameter by name
 - add to add a value to a parameter that is a list (e.g., cloud)
 - remove to remove a value from a parameter that is a list

See [settings.md](settings.md) for more details about configuration values that can
be defined in a configuration file directly, or on the command line.

The following example shows setting `cache_only` to true to always use the cache:

```bash
$ cloud-select config set:cache_only:true
```

Or to get a value:

```bash
$ cloud-select config get cache_only
```
```console
cache_only                     False
```

To remove (and add back) a cloud from the list:

```bash
$ cloud-select remove clouds aws
$ cloud-select add clouds aws
```

Note that a `:` between variables and values is also valid (e.g., to represent nesting).
To open the file in your config editor:

```bash
$ cloud-select config edit
```

which will first look at the environment variables `$EDITOR` and `$VISUAL` and will
fall back to the `config_editor` in your user settings (vim by default).

[home](/README.md#cloud-select)
