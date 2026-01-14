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

Put your pdfs in the `/pdfs`/ folder. There's an example in there from [The Shawville Equity](https://theequity.ca/) via the BANQ, but just two pages so that memory issues aren't at play if you're just trying things out; here's the [first issue](https://numerique.banq.qc.ca/patrimoine/details/52327/2553732?docsearchtext=1883). There is a text layer in the pdf from the BANQ, but it looks to have been done through an automatic process without human intervention, so images are sometimes askew and the underlying text is often very very poor indeed (look up the work of Ian Milligan on the consequences for research of bad newspaper OCR).

See the readme in the scripts folder for ways to tune the preprocessing script.
