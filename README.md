[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py3-PyHue?style=for-the-badge&logo=python&logoColor=green)](https://python.org)
[![PyPI](https://img.shields.io/pypi/v/py3-pyhue?label=py3-PyHue&logo=python&logoColor=green&style=for-the-badge)](https://pypi.org/project/py3-PyHue/)
[![DocsImage](https://img.shields.io/badge/Documentation-click%20here!-informational?style=for-the-badge)](https://jkam.notion.site/PyHue-6a7655a97f0249729a5dc729dd801cf0)
# Python3 Module for controlling Philips Hue lights.
## Quick Start Guide:
### Installation:
#### without VirtualENV:
```
python3 -m pip install py3-PyHue
```

#### with VirtualENV:
Windows:
```cmd
.\<envname>\Scripts\python.exe -m pip install py3-PyHue
```
Linux: 
```bash
./<envname>/bin/python3 -m pip install py3-PyHue
```

### Setup:
Here you have 2 options: Either the Auto-Discovery or the manual setting!

Auto-Discovery:
```python
    from py3_PyHue import Hue
    hue = Hue()
```
Manual:
```python
    from py3_PyHue import Hue
    hue = Hue(ip='<your ip address>')
```

Now a new instance of the Hue class is created. If you already used this package, you will notice, that the package will automagicaly connect to the Hue bridge. To restart the discovery process, stop the Python3 script and delete the file '.cached_ip_important' from the root directory (i.e. There, where the main script is located).

After a bridge was discovered, the authentication process will start. You will have to press the button on the front of the Bridge. After that, press the enter key to proceed. After this process you will have a new file '.cached_username_important' in the root directory.

#### Now you can start coding!
⠀
### Usage:
All of the available methods are described in the documentation! (It's linked above! You should really check it out!)

But for example, to toggle the light with the id '1', you can use the following code:
```python
    from py3_pyhue import Hue
    hue = Hue()
    hue.toggle_light(1)
```

To list all lights, you can use this!:
```python
    from py3_pyhue import Hue
    hue = Hue()
    print(hue.get_all_lights())
```

Finally, if you want to make custom API-Requests, you should use this:
```python
    from py3_pyhue import Hue
    hue = Hue()
    print(hue.api_request('<METHOD>', '<ENDPOINT>', <body (dict)>))
```

## Happy Coding!