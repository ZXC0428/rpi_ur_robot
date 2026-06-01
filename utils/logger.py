import logging

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # 建立控制台處理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # 建立檔案處理器
    fh = logging.FileHandler("claw_machine.log")
    fh.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    
    logger.addHandler(ch)
    logger.addHandler(fh)
