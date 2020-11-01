# nekodisp

apt install python3-lxml python3-pil libopenjp2-7-dev python3-numpy python-numpy libtiff5 libatlas-base-dev fonts-mplus


crontab -e
*/15 6-22 * * * /home/hoge/nekodisp/calenv.sh 1>/dev/null


lnetatmoのtimeoutが頻発するので .local/lib/python3.7/site-packages/lnetatmo.py の
def postRequest(url, params=None, timeout=10):
を
def postRequest(url, params=None, timeout=30):
に変更した。
