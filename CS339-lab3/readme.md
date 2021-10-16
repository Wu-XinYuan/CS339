# Readme

The file structure is:

```
├── CS.py :  C/S model using mininet
├── data.txt : file to transfer
├── recv	: store the file client receives
│   ├── h1.txt
│   ├── h2.txt
│   ├── h3.txt
│   ├── h4.txt
│   ├── h5.txt
│   └── h6.txt
├── report.pdf : report of this lab
├── server.log : the running log of server
├── server.py : implementation of server
├── client.py : implementation of client
└── thread.py : running C/S model using threads
```

If you want to test the C/S model, run `sudo python3 CS.py`, then the net will run, and the output of server will be written into `server.log` where you can see the time for downloading.

