# AWS Account Teardown

**WARNING!!!**

Deletes **ALL** resources in an AWS account

**WARNING!!!**

Well, "all" might be a slight exaggeration as some AWS services are not yet covered (please feel free to submit a PR to delete additional resource types).
But don't expect anything to be left if you call this script!

Usage:

Set up a virtual environment, activate it and install the dependencies:

```bash
pythnon3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Call the srcipt:

```bash
python teardown-all-resources.py
```

You might have to call the script several times (in case of resources not being successfully deleted because of dependencies, etc). If you spot an issue with a resource being deleted before its dependencies, please raise an issue or even better raise a PR.
