[Unit]
Description=Scanning | OCR for post and mail

[Service]
Type=simple
ExecStart=/home/uli/anaconda3/envs/datacenter/bin/python /opt/scanning -r ocrprocess
WorkingDirectory=/opt/scanning/
Restart=always
RestartSec=3

[Install]
WantedBy=sysinit.target
