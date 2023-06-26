# hra-amap

Code for AMap project. 

This repository aims to enable projection of tissue blocks registrered to a source organ to a new reference organ (usually the Human Reference Atlas, part of HuBMap). 

### Setup instructions:

1. Clone the repository with ```git clone https://github.com/cns-iu/hra-amap.git```

2. Clone the repository ```git clone https://github.com/ohirose/bcpd.git``` that implements the Bayesian Coherent Point Drift algorithm based on the following paper A Bayesian Formulation of Coherent Point Drift[https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=8985307]. The repository is ~1GB in file size hence it is not shipped with our repository and requires additional setup: 

    * For Windows

       1. No setup required.  

    * For MacOS and Linux

        1. Install the OpenMP and the LAPACK libraries if not installed. For MacOS, make sure XCode is installed. 

        2. Type ```make OPT=-DUSE_OPENMP ENV=<your-environment>```. Substitute ```<uyour-environment>``` with ```LINUX``` for Linux, ```HOMEBREW_INTEL``` for Intel Macs and ```HOMEBREW``` for Macs with Apple Silicon.

3. Ensure that the two repositories (hra-amap and bcpd) are at the **same root level**. 

4. To run a quick registration using the provided pipeline, please see ```notebooks/pipeline_usage``` 
