# Developer Guide

This is a short guide to help with development. We will expand it as we work
on automation for testing, etc.

## Documentation

The main documentation for the repository is in the [docs](https://github.com/converged-computing/cloud-select/tree/main/docs) directory,
and the interface itself is static and generated from the markdown with
javascript. The only programatically generated docs are in the [docs/api](https://github.com/converged-computing/cloud-select/tree/main/docs/api)
folder, which are currently done manually (and could be automated if desired). To update the api docs:

```bash
python -m venv env
source env/bin/activate
pip install -e .
cd apigen
```

Install dependencies to build the docs:

```bash
$ pip install -r requirements.txt
```

If you need to generate new source documents (given new structure):

```bash
$ sphinx-apidoc -o source/ ../cloud_select
```

And then to generate:

```bash
./apidoc.sh
```

And that's it! That script will build the docs, and then remove the old `docs/api`
folder to replace with the new one. If you want to test the build beforehand
(and look for errors or preview) you can do:

```bash
$ make html
$ cd _build/html
$ python -m http.server 9999
```

Then open your browser to [http://localhost:9999](http://localhost:9999)
to see the API docs You can use this same strategy of starting a local
server from within the docs folder to also preview the site.
