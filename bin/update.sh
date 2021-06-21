cd /Users/rodell/Documents/Arduino/docs
jupytext --to notebook /Users/rodell/Documents/Arduino/python/calibration.py
mv /Users/rodell/Documents/Arduino/python/calibration.ipynb /Users/rodell/Documents/Arduino/docs/source/
make clean
make html
git add . 
git commit -m "update website"
git push
