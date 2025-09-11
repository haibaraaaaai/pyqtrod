# PyQtRod

Software for visualization and analysis of rod data


## Install with pip from the Git directory


Install [Git for windows](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Clone the repository from the command line.

```
cd where_you_want_to_put_the_software
pip install git+https://github.com/Mriv31/pyqtrod.git
```

or form a virtual environnement :
Linux :

```
python -m venv pyqtrod_venv
source pyqtrod_venv/bin/activate  
```

Windows :


```
python -m venv pyqtrod_venv
.\testenv\Scripts\activate
```

Once in the virtual environnement just execute 

```
pyqtrod
```

### Update after new commits : 

```
pip install --no-cache-dir --force-reinstall git+https://github.com/Mriv31/pyqtrod
pip install --no-cache-dir --force-reinstall git+https://github.com/Mriv31/pynavgui

```
If needed, reinstall requirements
```
pip install --no-cache-dir --force-reinstall -r requirements.txt
```

## Install to be modified locally 


```
cd where_you_want_to_put_the_software
git clone git+https://github.com/Mriv31/pyqtrod
```

Yo will be asked to enter your physics credential. If there are any access problem, ask me and I will add permission for you to clone.

### Update the GIT directory

To update any modification I will have made to the software, just enter from the command line :

```
cd where_you_want_to_put_the_software/pyqtrod
git pull
```


### Install Python modules

Note : if in this part, in Windows, you get an error saying that windows can not find pip or python you need to add the Python path in your environment variables.

First upgrade the Python module manager pip :
```
pip install --upgrade pip
```

Several Python modules are needed to run the software. To do so open a command line console and enter :

```
cd where_you_want_to_put_the_software/pyqtrod
pip install -r requirements.txt
pip install -e pyqtrod
```
The ```-e``` flag allows you performing installing from the local folder instead of ding a copy and is thus needed for dev.

## Run PyQtRod

```
pyqtrod
```

## Load TDMS files

Click File "Load TDMS file"

## Summarize a folder speed and anisotropies

Click File "Summarize folder"

## Install Jupyter Notebook or Jupyter Lab for interactive data treatment
Execute from command-line :
```
pip install notebook
```
or, for Jupyter Lab,

```
pip install jupyterlab
```

## Launching jupyter notebook:
```
python -m notebook
```

or, for jupyterlab
```
python -m jupyterlab
```

You can find an example of jupyter notebook with treatment of Rod data in Examples.

## Troubleshoot

###Linux

OpenGL might not work perfectly (black screen on all openGL modules, 3D trajectories and AnisGL module).
It seems to be due to an incompatibility between PyOpenGL and Mesa (Intel drivers). It can be worked around if you have a nvidia card.
Either you only have a nvidia card and you shall not have that problem. If you have dual graphic cards, put the prime mode as "on demand" in NVIDIA settings, it will allow keep using the Intel card for common usage but ask for NVIDIA rendering for some applications.
```
sudo prime-query on-demand
```
Then execute the python application with env variable set to __GLX_VENDOR_LIBRARY_NAME=nvidia __NV_PRIME_RENDER_OFFLOAD=1.
```
__GLX_VENDOR_LIBRARY_NAME=nvidia __NV_PRIME_RENDER_OFFLOAD=1 python3 PyQtRod.py
```
If this does not work, you can also enforce the usage of nvidia graphic card all the time, but this will pump electricity.
```
sudo prime-query nvidia
```


## Third-Party Acknowledgment

This software uses the Qt frameworkfor its graphical user interface and other functionalities. Qt is available under the GNU Lesser General Public License (LGPL) version 3, and the GNU General Public License (GPL) version 2/3. The full texts of these licenses are included in the 'licenses' directory of this distribution.

Qt is a trademark of The Qt Company Ltd and is used under license. For more information on Qt, please visit [Qt's official website](https://www.qt.io/).


## Authors and acknowledgment
TODO
## License
TODO
## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
## For Martin 
