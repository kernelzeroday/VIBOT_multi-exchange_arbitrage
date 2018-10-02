

MQ_USER = 'u8mqGooxldO264DN5tse2jIesV9PfJjxFvNbI0xR39HY3aBXsRZiYxmfhkSmT1Jp'
MQ_PASS = None


PID_FILE = 'last_pisd.json'


SERVER_MARKER = 'vi1'

SCRAPER_PATH = 'scrapper/'
SCRAPER_RUN_CMD = './scraper'

TRADE_ENGINE_PATH = 'order_engine/'
TRADE_ENGINE_RUN_CMD = './trade_current.py'

BALANCE_ENGINE_PATH = 'balance_engine/'
BALANCE_ENGINE_RUN_CMD = './start.sh'

ORDER_TRACKING_ENGINE_PATH = 'order_tracking_engine/'
ORDER_TRACKING_ENGINE_RUN_CMD = '/OrderTrack.py'

TRANSFER_PATH = 'transfer/'
TRANSFER_RUN_CMD = './start.sh'

LOG_ENGINE_PATH = ''  # todo: where is located Log Engine?
LOG_ENGINE_RUN_CMD = ''


CMD_MAP = {
    "test": {
        'path': 'engine_manager/',
        'run_cmd': 'python scropt_example.py'},
    "scraper": {
        'path': SCRAPER_PATH,
        'run_cmd': SCRAPER_RUN_CMD},
    "trade_engine": {
        'path': TRADE_ENGINE_PATH,
        'run_cmd': TRADE_ENGINE_RUN_CMD},
    "balance_engine": {
        'path': BALANCE_ENGINE_PATH,
        'run_cmd': BALANCE_ENGINE_RUN_CMD},
    "order_tracking": {
        'path': ORDER_TRACKING_ENGINE_PATH,
        'run_cmd': ORDER_TRACKING_ENGINE_RUN_CMD},
    "transfer": {
        'path': TRANSFER_PATH,
        'run_cmd': TRANSFER_RUN_CMD},
    "log_engine": {
        'path': LOG_ENGINE_PATH,
        'run_cmd': LOG_ENGINE_RUN_CMD}}
