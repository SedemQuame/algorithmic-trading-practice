import os
import logging
import asyncio
import argparse
import pprint
import collections
from deriv_api import DerivAPI
import deriv_api.errors
from dotenv import load_dotenv
from MomentumTrader import MomentumTrader

load_dotenv()


async def buy_proposal(api, proposal, price):
    proposal_id = proposal.get("proposal").get("id")
    buy = await api.buy({"buy": proposal_id, "price": int(price)})
    return buy


async def sell_proposal(api, proposal, price):
    proposal_id = proposal.get("proposal").get("id")
    sell = await api.sell({"buy": proposal_id, "price": int(price)})
    return sell


async def run_trading_logic(api, contracts, arguments):
    trader = MomentumTrader(api, arguments, contracts)
    await trader.trading_logic()

async def risk_management_logic(api, active_contracts):
    while True:
        print("\n" + "*" * 30)
        print("Risk logic.")
        print("*" * 30)

        pprint.pprint(active_contracts)
        # Check PNL on all active contracts
        for contract_info in active_contracts:
            if contract_info['status'] == "active":
                try:
                    contract_info = await api.proposal_open_contract()
                    pnl = contract_info['proposal_open_contract']['profit']
                    contract_id = contract_info['proposal_open_contract']['contract_id']
                    req_id = contract_info['req_id']
                    sell_contract = {
                        'price': 0,
                        'req_id': req_id,
                        'sell': contract_id,
                    }
                    # Exit trade if momentum of contract price has approached the calculated_loss
                    if pnl <= -0.40:
                        logging.info(
                            "Risk management:- Sell the contract, when pnl is -0.40.")
                        await api.sell(sell_contract)
                    if pnl >= 0.50:
                        logging.info(
                            "Risk management:- Sell the contract, when pnl is 0.50.")
                        await api.sell(sell_contract)
                except deriv_api.errors.ResponseError as e:
                    print("Error occurred:", str(e))
        print("\n")
        await asyncio.sleep(5)


async def run_tasks(api, arguments):
    contracts = collections.deque([])
    risk_task = asyncio.create_task(risk_management_logic(api, contracts))
    trading_task = asyncio.create_task(
        run_trading_logic(api, contracts, arguments))
    await asyncio.gather(trading_task, risk_task)


async def main(arguments):
    # Deriv API endpoint and app_id
    app_id = os.getenv("APP_ID")
    api_token = os.getenv("DERIV_API")

    # Connect to Deriv API
    api = DerivAPI(app_id=app_id)
    await api.authorize(api_token)

    print(arguments.symbol, arguments.proposal_amount, arguments.amount, arguments.duration)
    await run_tasks(api, args)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", default="R_100", choices=['1HZ10V', 'R_10', '1HZ25V', 'R_25', '1HZ50V', 'R_50', '1HZ75V', 'R_75', '1HZ100V', 'R_100', '1HZ150V', '1HZ250V', 'OTC_DJI'])
    parser.add_argument("-p", "--proposal_amount", default=1, type=int)
    parser.add_argument("-a", "--amount", default=2, type=int)
    parser.add_argument("-d", "--duration", default=240, type=int)
    parser.add_argument("-t", "--target", default=2, type=int)
    args = parser.parse_args()
    asyncio.run(main(args))
