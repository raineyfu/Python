CD /d "%~dp0"

start "NetBot-Server" cmd /K py -3 src/netbots_server.py -p 20000 -bots 6 -stepsec 0.05 -games 100 -stepmax 3000

start "hideincorner" cmd /K py -3 robots/hideincorner.py -p 20002 -sp 20000
start "lighthouse" cmd /K py -3 robots/lighthouse.py -p 20003 -sp 20000
start "scaredycat" cmd /K py -3 robots/scaredycat.py -p 20004 -sp 20000
start "raineyfuv3" cmd /K py -3 robots/raineyv3.py -p 20005 -sp 20000
start "raineyfu" cmd /K py -3 robots/rainey.py -p 20006 -sp 20000
start "raineyfuv2" cmd /K py -3 robots/raineyv2.py -p 20007 -sp 20000


start "NetBot-Viewer" cmd /K py -3 src/netbots_viewer.py -p 20001 -sp 20000
