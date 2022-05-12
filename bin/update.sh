cd /Users/rodell/Documents/Arduino/docs
jupytext --to notebook /Users/rodell/Documents/Arduino/scripts/calibration.py
mv /Users/rodell/Documents/Arduino/scripts/calibration.ipynb /Users/rodell/Documents/Arduino/docs/source/
make clean
make html
git add . 
git commit -m "update website"
git push
