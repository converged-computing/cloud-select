# Clouds

Cloud Select supports the following clouds. Note that currently, to generate your own updated cache of
data you'll need to provide credentials for each. We are hoping to provide automation at some point
that is updated nightly so this isn't required.

## Google Cloud

For Google Cloud, you can generally [provide your default credentials](https://cloud.google.com/docs/authentication/client-libraries)

```bash
$ gcloud auth application-default login
```

to be discovered by the client. **You will need to enable the billing and compute APIs.**

## Amazon Web Services (AWS)

Amazon web services typically works by way of exporting credentials to the environment.
We use boto3, so you can expect to export [these credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables).
Note that it often is a different level of permission (IAM) to get access to billing,
so look into IAM if you are able to retrieve instances but not billing.

[home](/README.md#cloud-select)
