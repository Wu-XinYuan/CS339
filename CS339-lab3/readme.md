# Readme

The file structure is:

```
├── CS.py :  C/S model using mininet
├── P2P.py :  P2P model using mininet
├── data.txt : file to transfer
├── recv	: store the file client receives
│   ├── h1.txt
│   ├── h2.txt
│   ├── h3.txt
│   ├── h4.txt
│   ├── h5.txt
│   ├── h6.txt
│   ├── h1_p2p.txt
│   ├── h2_p2p.txt
│   ├── h3_p2p.txt
│   ├── h4_p2p.txt
│   ├── h5_p2p.txt
│   └── h6_p2p.txt
├── report.pdf : report of this lab
├── server.log : the running log of server from CS.py
├── server_p2p.log : the running log of server from P2P.py
├── server.py : implementation of server
├── server_p2p.py : implementation of server for p2p model
├── client.py : implementation of client
├── client_p2p.py : implementation of client for p2p model
└── thread.py : running C/S model using threads
```

If you want to test the C/S model, run `sudo python3 CS.py`, then the net will run, and the output of server will be written into `server.log` where you can see the time for downloading.

Similarly, If you want to test the P2P model, run `sudo python3 P2P.py`, then the net will run, and the output of server will be written into `server_p2p.log` .

