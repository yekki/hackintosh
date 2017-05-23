import logging, click, os

RECORDER = True

logging.basicConfig(level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')

_recoder = logging.getLogger('recorder')
_recoder.setLevel(logging.INFO)

_handler = logging.FileHandler(os.path.join(os.getcwd(), 'recorder.log'), mode='w')
_handler.setLevel(logging.INFO)
_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))

# add the handlers to the logger
_recoder.addHandler(_handler)


def info(msg):
    logging.info(click.style(msg, fg='blue'))


def warning(msg):
    logging.warning(click.style(msg, fg='yellow'))


def error(msg):
    logging.error(click.style(msg, fg='magenta'))


def critical(msg):
    logging.critical(click.style(msg, fg='red'))
    exit(-1)


def record(msg):
    pass
    #_recoder.info(msg)
