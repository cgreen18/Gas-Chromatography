With Python 2 depreciated, it's important to assure Python 3 is used.

### Virtual Environment

Install virtualenv
'''
pip install virtualenv
'''

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

'''
python3 -m venv gc
'''

Update pip and tools for building a wheel (for use later)

'''
pip install -U pip
pip install -U six wheel setuptools
'''


