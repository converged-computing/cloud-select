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

You can do a "one off" request to not use the cache:

```bash
$ cloud-select instance --memory 4 --no-cache
```

Ask for a specific cloud on the command line (note you can also ask via your settings.yml configuration file for a more permanent default):

```bash
$ cloud-select instance --cloud google --cpus-min 200 --cpus-max 400
```

As for an aws instance that supports efa networking, and support least to most expensive.

```bash
$ cloud-select instance --cloud aws --efa --sort price --asc
```

Note that we don't have support for all attributes defined yet! By default, you won't be allowed
to filter for a property that we cannot derive:

```bash
$ cloud-select instance --disk-type ssd
AmazonInstance does not support getting information about disk_type. Set allow_missing_attributes in your settings.yml to 'true' to continue anyway.
```

If you want to disable this and do the query anyway (and if another cloud supports it, you will get results) you can follow the instructions in the message above. We are doing our best to add support for the most attributes we can soon!

### Sorting

By default we sort results based on the order the solver produces them.
However, you can ask to sort your results by an attribute, e.g., here is memory:

```bash
$ cloud-select instance --sort-by memory
```

By default, when sort is enabled on an attribute we do descending, so the largest values
are at the top. You can ask to reverse that with `--asc` for ascending, meaning we sort
from least to greatest:

```bash
$ cloud-select instance --asc --sort-by memory
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
$ cloud-select instance --region east
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
you can set `cache_only` in your settings.yml to true (or false to disable it):

```yaml
cache_only: true
```

### Debugging

To debug, you can add `--debug` to see the database query that is done:

```bash
$ cloud-select --debug instance
```

### Frequently Asked Questions

> What happens if I ask for a filter that isn't defined for a cloud?

Let's say you want to ask for a property that is defined for AWS but not Google Cloud.
If your `settings.yml` property "allow_missing_attributes" is false and you are trying
to query both clouds, you'll get an error. At this point you have two choices - you
can either set this to true (and the not supporting cloud likely won't match the query)
or you can run a query specific to the cloud that has it (e.g., adding `--cloud`).

> What if an instance has the function to get the attribute, but it returns nothing?

We assume in these cases that the instance does not support or have information
for what you are asking for, so we don't generate a fact for it. If you are explicitly
asking for this feature in your query, you likely won't see the instance in the result.
If you aren't interested in the attribute then you could still see it as a result.

> Where do prices come from?

For AWS, we use the API. For Google Cloud, we currently get a page from the web.
Thus, Google Prices represent Iowa (us-central-1) and should be used as estimates only.
We need a few things to be able to support using the Google API - namely the lab
to support having an account we can authenticate from actions to support the cache.

## config

If you want to edit a configuration value, you can either edit the [cloudselect/settings.yml](https://github.com/converged-computing/cloud-select/blob/main/cloudselect/settings.yml).
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

## cache

Since API calls are expensive (and often take a long time) we try to cache
as much data as possible to be retrieved without needing to use a credential
or wait for the request. Toward this aim, we have the `cache` command group
to interact with your local cache.

### clear
First, to manually clear the cache, deleting the entire cache directory:

```bash
$ cloud-select cache --clear
```

Don't ask for a prompt!

```bash
$ cloud-select cache --clear --force
```

### update

If you want to force an update:

```bash
$ cloud-select cache --update
```

### push

Or push to an OCI registry with [oras](https://oras.land) (this means a .tar.gz artifact and manifest with content types).
This command requires you to export a registry username and token password for basic authentication:

```bash
export ORAS_USER=mygithub
export ORAS_PASS=myGitHubToken
```

And then just push! The default will push what you currently have available in the cache.

```bash
$ cloud-select cache --push ghcr.io/converged-computing/cloud-select-cache:latest
```

For media type, we use the suggested format of reverse organization name, then our own
namespace of identifiers for the tool. E.g.,:

- 'org.llnl.gov.cloud-select.google.prices' Google cache data for prices
- 'org.llnl.gov.cloud-select.google.instances' Google cache data for instance
- 'org.llnl.gov.cloud-select.aws.prices' AWS cache data for prices
- 'org.llnl.gov.cloud-select.aws.instances' AWS cache data for instance

These will correspond to the media types for the layers. For example:

```python
{'aws/instances.json': 'org.llnl.gov.cloud-select.aws.instances',
 'aws/prices.json': 'org.llnl.gov.cloud-select.aws.prices',
 'google/instances.json': 'org.llnl.gov.cloud-select.google.instances',
 'google/prices.json': 'org.llnl.gov.cloud-select.google.prices'}
```

Note that (as you can see above) these flags can be used together. The order of operations is as follows:

- clear
- update
- push

It wouldn't make sense to clear and push without an update, so use your noggin when specifying what
you want to do. Finally, for cases where you are running this in a CI context and expect
all data to be retrieved, set the `--require-all` flag:

```bash
$ cloud-select cache --push ghcr.io/converged-computing/cloud-select-cache:nightly --require-all
```

[home](/README.md#cloud-select)
