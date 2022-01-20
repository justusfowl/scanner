# Scanner
Repository to create a docker container watching a directory, creating sandwich / OCRed documents and uploading them to a sharepoint document library. 

docker run -it  -v /home/uli/dev/scanning/mondir:/mondir -v /home/uli/dev/scanning/config.json:/config.json ukasys/scanner

Necessary provisions: 
* config.json file 
* mount the directory that shall be watched for pdf-file creations