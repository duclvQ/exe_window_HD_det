# install pyinstaller and other libs
pip install pyinstaller, ultralytics, opencv-python, numpy, gputil, Pillow

# the exsist predict.spec was fixed to run correctlly, do not create new one
pyinstaller predict.spec
