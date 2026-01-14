# newspaper_utilities
Some scripts for working with scans of historical newspapers

Quick start using Google Colab:

```
!git clone https://github.com/XLabCU/newspaper_utilities.git
!pip install -r /content/newspaper_utilities/scripts/requirements.txt
!apt-get install -y poppler-utils
#after restart
%cd newspaper_utilities
!python scripts/preprocess.py
!python scripts/process_images_surya_batch.py
```
