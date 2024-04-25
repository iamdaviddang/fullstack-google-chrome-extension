l
ll
cd pyBoardFRUcopy.lnk 
ls
cd pyBoardFRUcopy
cd D:
cd YAMA/pyBoardFRU
pwd
exit
pip list
pip freeze | xargs pip uninstall -y
pip list
cd D:
cd YAMA/pyBoardFRU/
pip install -r requirements.txt 
python getIP.py EWCR001003
pip list
python getIP.py EWCD003689
exit
cd D:
cd YAMA/pyBoardFRU/
ls -a
rm -rf .gitconfig 
la -a
ls -a
exit
ls -la
pwd
cd D:
cd YAMA/pyBoardFRU/
code .
cd iRMC-Tools/
py .\powerOff 172.25.161.244
ll
python powerOff 172.25.161.244
python powerOff 172.25.161.244
ll
python reboot 172.25.161.244
python powerOff 172.25.161.244
python reboot 172.25.161.244
python powerOff 172.25.161.244
python reboot 172.25.161.244
python powerOff 172.25.161.244
cls
python reboot 172.25.161.244
python reboot 172.25.161.244
python powerOff 172.25.161.244
python powerOff 172.25.161.244
clear
python changeDefaultPW.py
python changeDefaultPW.py
python changeDefaultPW.py
ssh davidd@172.25.8.2
ll
python reboot-and-powerOn.py 172.25.161.244
python powerOff.py 172.25.161.244
python powerOff.py 172.25.161.244
python reboot-and-powerOn.py 172.25.161.244
python powerOff.py 172.25.161.244
python reboot-and-powerOn.py nic
python reboot-and-powerOn.py nic
python reboot-and-powerOn.py 172.
python reboot-and-powerOn.py 172.
python PowerStatus.py 
pip install Office365-REST-Python-Client
cd ..
echo "# fru_irmc_tools" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/iamdaviddang/fru_irmc_tools.git
git add .
git push -u origin main
ll
cd ..
git init
git status
git add pyBoardFRU/
git status
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/iamdaviddang/fru_irmc_tools.git
git push -u origin main
cd pyBoardFRU/
ls -la
rm -rf .git
ls -la
exit
cd /d/YAMA/pyBoardFRU/
py main.py 
exit
