from ocrmac import ocrmac

# This uses the Apple Vision Framework built into your Mac
# It is extremely fast and accurate on M1.
annotations = ocrmac.OCR("data/preprocessed/83471_1888-10-25/83471_1888-10-25_p02_c04_s004_pt0.jpg").recognize()

for text, confidence, bbox in annotations:
    print(f"[{confidence:.2f}] {text}")