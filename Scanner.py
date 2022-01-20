# %%
import logging

import office365
from shareplum import Site, Office365
from shareplum.site import Version
import json, os
from pathlib import Path
import shutil
import glob
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# %%
# https://github.com/iamlu-coding/python-upload2sharepoint/blob/main/sharepoint.py

# %%
logging.basicConfig()
logger = logging.getLogger("OCRScanner")
logger.setLevel(logging.DEBUG)
logger.info("Test")

# %%
class SharepointFile: 
    
    def __init__(self):
        config_path = Path(os.getcwd()) / "config.json"

        # read config file
        with open(config_path) as config_file:
            config = json.load(config_file)
            config = config['share_point']

        USERNAME = config['user']
        PASSWORD = config['password']
        SHAREPOINT_URL = config['url']
        SHAREPOINT_SITE = config['site']
        SHAREPOINT_DOC = config['doc_library']
        
        self.authcookie = Office365(SHAREPOINT_URL, username=USERNAME, password=PASSWORD).GetCookies()
        self.site = Site(SHAREPOINT_SITE, version=Version.v365, authcookie=self.authcookie)
       
    def upload_file_to_sp_mailbox(self, file_path, mailbox_dir=""):
        
        
        if len(mailbox_dir) < 1:
            mailbox_dir = '/'.join(["Scans", "Mailbox"])

        folder = self.site.Folder(mailbox_dir)

        file_name = os.path.basename(file_path)

        with open(file_path, mode='rb') as file_obj:
            file_content = file_obj.read()

        folder.upload_file(file_content, file_name)

# %%
class Watcher:
    
    def __init__(self, watch_directory):
        
        self.watch_directory = watch_directory
        self.observer = Observer()
        logger.info("Starting to watch (non-recursive): %s" % self.watch_directory)

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.watch_directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            logger.error("Error")

        self.observer.join()

# %%
class Handler(FileSystemEventHandler):
    
    def mk_tmp_dir(self, file_path):
        directory = Path(file_path).parent
        tmp_dir = directory.joinpath(".processing")
    
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        
        return tmp_dir
    
    @staticmethod
    def mv_file(file_path, tmp_dir):
        
        time.sleep(2)
        
        file_name = os.path.basename(file_path)
        process_path = tmp_dir / file_name
        shutil.move(file_path, process_path)
        
        return process_path
    
    def clean_up(self, directory, file_name):
            
        fileList = glob.glob(str(Path(directory) / ( file_name + "*"))    , recursive=True)
        
        # Iterate over the list of filepaths & remove each file.
        for filePath in fileList:
            try:
                os.remove(filePath)
            except OSError:
                logger.error("Error while deleting file %s" % filePath)
                
    @staticmethod
    def created_end(file_path):
        init_size = Path(file_path).stat().st_size
        time.sleep(2)
        init_size_2 = Path(file_path).stat().st_size

        if init_size == init_size_2:
            return True
        else:
            return False
    
    def sandwich_pdf(self, file_path):        
        file_name = Path(file_path).stem
        
        tiff_path = Path(file_path).parent / (file_name + ".tiff")
        
        convert_cmd = 'gs -dNOPAUSE -q -r600 -sCompression=lzw -sDEVICE=tiff48nc -sPAPERSIZE=a4 -dBATCH -sOutputFile={TIFF_PATH} {IN_FILE_PATH}'.format(
            TIFF_PATH=tiff_path, 
            IN_FILE_PATH=file_path
        )
        
        logger.info(convert_cmd)
        conversion = os.system(convert_cmd)
        
        file_name_base = (file_name + "-ocr")
        out_path = Path(file_path).parent / file_name_base
        out_file_path = Path(file_path).parent / (file_name_base + ".pdf")
        
        pdf_cmd = 'tesseract {TIFF_PATH} {PDF_OUT_PATH} pdf'.format(
            TIFF_PATH=tiff_path, 
            PDF_OUT_PATH=out_path
        )
        
        logger.info(pdf_cmd)
        res = os.system(pdf_cmd)
        
        spFile = SharepointFile()
        
        spFile.upload_file_to_sp_mailbox(
            file_path=out_file_path
        )
        
        self.clean_up(Path(file_path).parent, Path(file_name).stem)
        
        logger.info("Completed for file %s" % file_path)
    
    def on_any_event(self, event):
        
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            logger.info("Received created event - %s." % event.src_path)
            
            while not self.created_end(event.src_path):
                logger.info("Not complete yet - %s" % event.src_path)
                time.sleep(0.5)
                
            logger.info("File seems to be complete - %s." % event.src_path)
            
            tmp_dir = self.mk_tmp_dir(event.src_path)
            
            process_path = self.mv_file(event.src_path, tmp_dir)
            
            logger.info(process_path)
            
            self.sandwich_pdf(process_path)

if __name__ == "__main__":

    env_mon_dir = os.environ.get('MONITORING_DIRECTORY')
    if env_mon_dir is None:
        env_mon_dir = Path(os.getcwd()) / "mondir"

    w = Watcher(watch_directory = env_mon_dir)

    w.run()