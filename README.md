# TerraByte_Client
 A client to download data from the TerraByte Portal
 
## The TerraByte Project
https://terrabyte.acs.uwinnipeg.ca/index.html

## Tutorials/Manuals
Video Tutorial:

https://youtu.be/2MX4ascCTq0

Written Manual and Parameter Explanation: 

https://terrabyte.acs.uwinnipeg.ca/assets/programs/TB_Client_Manual.pdf

## Installation
### Executable (Windows only)
https://terrabyte.acs.uwinnipeg.ca/assets/programs/client_app.zip

Instructions: 
Download and unpack the zip to a folder of your choice. 
Find and execute the file "client_app.exe". 

Remember, that you will have to login with your user-credentials provided by an admin, before you can do anything. Subsequent usage does not require to login again. 

Be beware that by once logged in your login credentials are saved within the file "parameters.json" (which will be created on first start of the program). If you copy the folder containing the program you will thus also copy your credentials!

### Python 3.7 (Unix, Windows, Mac)
Instructions: 
Download this repo and create a Python environment (Python 3.7) to use it in. Install the listed dependencies. Then run: `client_app.py`
Dependencies: 
* wx: https://www.wxpython.org/
* pandas: https://pandas.pydata.org/
* requests: https://docs.python-requests.org/en/latest/
* certifi: https://pypi.org/project/certifi/

## Citation/Giving Credit
If you enjoy the data downloaded by the TerraByte Client and/or use our data for your research give credit by citing: 

https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0243923

```
@article{10.1371/journal.pone.0243923,
    doi = {10.1371/journal.pone.0243923},
    author = {Beck, Michael A. AND Liu, Chen-Yi AND Bidinosti, Christopher P. AND Henry, Christopher J. AND Godee, Cara M. AND Ajmani, Manisha},
    journal = {PLOS ONE},
    publisher = {Public Library of Science},
    title = {An embedded system for the automated generation of labeled plant images to enable machine learning applications in agriculture},
    year = {2020},
    month = {12},
    volume = {15},
    url = {https://doi.org/10.1371/journal.pone.0243923},
    pages = {1-23},
    number = {12},
}
```
