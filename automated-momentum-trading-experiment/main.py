import os
import time
import logging
import asyncio
import argparse
import pprint
from datetime import datetime
from deriv_api import DerivAPI
from dotenv import load_dotenv

load_dotenv()


async def buy_proposal(api, proposal, price):
    proposal_id = proposal.get("proposal").get("id")
    buy = await api.buy({"buy": proposal_id, "price": int(price)})
    return buy


async def sell_proposal(api, proposal, price):
    proposal_id = proposal.get("proposal").get("id")
    sell = await api.sell({"buy": proposal_id, "price": int(price)})
    return sell


async def trading_logic(api, contracts, symbol, proposal_amount, amount, duration):
    # Initialize variables
    last_price = None
    prev_price = None
    last_time = None
    curr_time = None
    account = await api.balance()
    intial_balance = account["balance"]["balance"]

    # Momentum strategy parameters
    threshold = 0.7
    while True:
        print("Trading logic.")
        print("*" * 30)
        account = await api.balance()
        curr_balance = account["balance"]["balance"]
        print(f"Current account balance: {curr_balance}")
        if curr_balance > intial_balance / 2:
            # Receive data from Deriv API
            proposal = await api.proposal(
                {
                    "proposal": proposal_amount,
                    "amount": amount,
                    "barrier": "+0.1",
                    "basis": "payout",
                    "contract_type": "PUT",
                    "currency": "USD",
                    "duration": duration,
                    "duration_unit": "s",
                    "symbol": symbol,
                }
            )
            if "spot" in proposal["proposal"]:
                # Get the latest candle data
                price = proposal["proposal"]["spot"]
                # Check if it's a new trading period
                curr_time = datetime.utcfromtimestamp(proposal["proposal"]["spot_time"])
                if last_time is None or (curr_time - last_time).seconds >= 60:
                    last_time = curr_time
                    if last_price is not None and prev_price is not None:
                        # Calculate momentum
                        momentum = last_price - prev_price
                        logging.info(f"Momentum: {momentum}")

                        # Check if momentum is positive
                        if momentum > 0:
                            call_proposal = await api.proposal(
                                {
                                    "proposal": proposal_amount,
                                    "amount": amount,
                                    "barrier": "+0.10",
                                    "basis": "payout",
                                    "contract_type": "CALL",
                                    "currency": "USD",
                                    "duration": duration,
                                    "duration_unit": "s",
                                    "symbol": symbol,
                                    # "limit_order": {
                                    #     "take_profit": (amount / 2),
                                    # }
                                }
                            )
                            if (
                                "error" not in call_proposal
                                and "proposal" in call_proposal
                            ):
                                logging.info(
                                    f"Trading:- possible buy @ {threshold * (last_price - price)}"
                                )
                                # Buy if momentum is greater than threshold
                                if momentum >= threshold * (last_price - price):
                                    # Place buy order
                                    logging.info(f"Trading:- buy @ {price}")
                                    contracts.append(await buy_proposal(api, call_proposal, price))

                        # Check if momentum is negative
                        elif momentum < 0:
                            put_proposal = await api.proposal(
                                {
                                    "proposal": proposal_amount,
                                    "amount": amount,
                                    "barrier": "-0.10",
                                    "basis": "payout",
                                    "contract_type": "PUT",
                                    "currency": "USD",
                                    "duration": duration,
                                    "duration_unit": "s",
                                    "symbol": symbol,
                                    # "limit_order": {
                                    #     "take_profit": (amount / 2),
                                    # }
                                }
                            )
                            if (
                                "error" not in put_proposal
                                and "proposal" in put_proposal
                            ):
                                logging.info(
                                    f"Trading:- possible sell @ {threshold * (last_price - price)}"
                                )
                                # Sell if momentum is less than threshold
                                if abs(momentum) >= threshold * (price - last_price):
                                    # Place sell order
                                    pass
                                    # logging.info(f"Trading:- sell @ {price}")
                                    # contracts.append(await buy_proposal(api, put_proposal, price))

                print("Trading:- Current contracts.")
                pprint.pprint(contracts)

                # Update previous and last price
                prev_price = last_price
                last_price = price

                print(f"Last time: {last_time}, Current time: {curr_time}")
                print(f"Previous price: {prev_price}, Last price: {last_price}")
                print("*" * 80 + "\n\n")
            else:
                logging.info("Current algorithm, is ")
        await asyncio.sleep(5)


async def risk_management_logic(api, active_contracts):
    calculated_loss = 0
    trailing_stop_loss = 0
    while True:
        print("Risk logic.")
        print("*" * 30)
        # Get active contracts
        account = await api.balance()
        # Check PNL on all active contracts
        for contract in active_contracts:
            proposal_id = contract.get('id')
            proposal_info = await api.proposal_open_contract()
            # cancel
            # contract_update
            # contracts_for

            buy_price = proposal_info['proposal_open_contract']['buy_price']
            current_price = proposal_info['proposal_open_contract']['spot']
            pnl = proposal_info['proposal_open_contract']['profit']
            
            # Check momentum of contract price
            momentum = current_price - trailing_stop_loss
            print(f"Risk management:- {momentum}")
            
            # Exit trade if momentum of contract price has approached the calculated_loss
            if pnl <= calculated_loss:
                logging.info(f"Risk management:- Exiting trade for proposal {proposal_id} to minimise stop loss")
                await api.sell({"sell": proposal_id, "price": current_price})
            
            # Move trailing stop loss up if momentum of contract price is performing well in profit state
            elif pnl > 0 and momentum > 0:
                logging.info(f"Risk management:- Moving trailing stop loss to price {current_price}")
                trailing_stop_loss = current_price
        await asyncio.sleep(5)


async def run_tasks(api, contracts, symbol, proposal_amount, amount, duration):
    risk_task = asyncio.create_task(risk_management_logic(api, contracts))
    trading_task = asyncio.create_task(trading_logic(api, contracts, symbol, proposal_amount, amount, duration))
    await asyncio.gather(trading_task, risk_task)
    # await asyncio.gather(risk_management_logic(api, contracts), trading_logic(api, contracts, symbol, proposal_amount, amount, duration))


async def main(symbol, proposal_amount, amount, duration):
    # Deriv API endpoint and app_id
    app_id = os.getenv("APP_ID")
    api_token = os.getenv("DERIV_API")
    contracts = []

    # Connect to Deriv API
    api = DerivAPI(app_id=app_id)
    await api.authorize(api_token)

    print(symbol, proposal_amount, amount, duration)
    await run_tasks(api, contracts, symbol, proposal_amount, amount, duration)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", default="R_100", choices=['1HZ10V', 'R_10', '1HZ25V', 'R_25', '1HZ50V', 'R_50', '1HZ75V', 'R_75', '1HZ100V', 'R_100', '1HZ150V', '1HZ250V', 'OTC_DJI'])
    parser.add_argument("-p", "--proposal", default=1, type=int)
    parser.add_argument("-a", "--amount", default=2, type=int)
    parser.add_argument("-d", "--duration", default=240, type=int)
    args = parser.parse_args()
    asyncio.run(main(args.symbol, args.proposal, args.amount, args.duration))
