import asyncio
import logging

from glQiwiApi import QiwiWrapper, types
from glQiwiApi.core.web_hooks.config import Path

path = Path(
    transaction_path="/qiwi_hook"
)

TOKEN = 'b8dd85a71e90b8cb41749faa28f162fe'
SECRET_P2P = 'eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6ImJuMXZmNy0wMCIsInVzZXJfaWQiOiIzODA5NjgzMTc0NTkiLCJzZWNyZXQiOiI4ZjI4NGVjYWQ0ZTE0Y2MwYzA5ZTRlOWNiNTJjM2Q3MzU2NGVjMWQxZDYyNWIwZDZhMTQ3NjIyZDEyZTJmNWFlIn19'
WALLET_NUM = '+380968317459'
REG_WEBHOOK = True

wallet = QiwiWrapper(
    api_access_token=TOKEN,
    secret_p2p=SECRET_P2P,
    without_context=True,
    phone_number=WALLET_NUM
)


@wallet.transaction_handler(lambda event: ...)
async def get_transaction(event: types.WebHook):
    print(event)


@wallet.bill_handler()
async def fetch_bill(notification: types.Notification):
    print(notification)

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
wallet.bind_webhook(
    delete_old=True
)
if __name__ == '__main__':
    # if REG_WEBHOOK:
    #     asyncio.get_event_loop().run_until_complete(reg_webhook())
    # wallet.start_webhook(
    #     port=8080,
    #     level=logging.INFO,
    #     format=FORMAT,
    #     host="0.0.0.0"
    # )
    wallet.start_webhook(
        path=path
    )
