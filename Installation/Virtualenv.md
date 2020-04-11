With Python 2 depreciated, it's important to assure Python 3 is used.

### Virtual Environment

Install virtualenv
```
pip install virtualenv
```

Test that virtualenv setup the executable correctly by typing

```
virtualenv
```

If the manual does not appear then you must add the executable to your .bashrc (not the only method but it's simple) and reload the profile.

```
echo -e '\nexport PATH="/home/$USER/.local/bin:$PATH"' >> ~/.bashrc
source .bashrc
```

### Build Python 3 environment
system-site-packages flag is passed because I found an error about some library missing in the venv but it was present in the system shared python files.
```
python3 -m venv --system-site-packages .gc_venv
```
