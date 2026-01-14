# newspaper_utilities
Some scripts for working with scans of historical newspapers

Quick start using Google Colab:

```
!git clone https://github.com/shawngraham/jan11_exp.git
!pip install -r /content/jan11_exp/scripts/requirements.txt
!apt-get install -y poppler-utils
#after restart
%cd jan11_exp
!python scripts/preprocess.py
!python scripts/process_images_surya_batch.py
```
