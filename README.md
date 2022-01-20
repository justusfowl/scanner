# Scanner
Repository to create a docker container watching a directory, creating sandwich / OCRed documents and uploading them to a sharepoint document library. 

docker build -t justusfowl/scanner .

docker run -it  -v /home/uli/dev/scanning/mondir:/mondir -v /home/uli/dev/scanning/config.json:/config.json justusfowl/scanner

docker run -d --restart unless-stopped  -v /data/scans:/mondir -v /home/uli/scanner/config.json:/config.json justusfowl/scanner



Necessary provisions: 
* config.json file 
* mount the directory that shall be watched for pdf-file creations