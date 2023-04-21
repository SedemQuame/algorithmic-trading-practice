import os
import time
import logging
import asyncio
import argparse
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


async def main(symbol, proposal_amount, amount, duration):
    # Deriv API endpoint and app_id
    app_id = os.getenv("APP_ID")
    api_token = os.getenv("DERIV_API")

    # Initialize variables
    last_price = None
    prev_price = None
    last_time = None
    curr_time = None

    # Momentum strategy parameters
    threshold = 0.5

    # Connect to Deriv API
    api = DerivAPI(app_id=app_id)
    await api.authorize(api_token)

    account = await api.balance()
    intial_balance = account["balance"]["balance"]
    # symbols = ['1HZ10V', 'R_10', '1HZ25V', 'R_25', '1HZ50V', 'R_50', '1HZ75V', 'R_75', '1HZ100V', 'R_100', '1HZ150V', '1HZ250V', 'OTC_DJI']

    print(symbol, proposal_amount, amount, duration)
    while True:
        account = await api.balance()
        curr_balance = account["balance"]["balance"]
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
                # print(curr_time)
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
                                    "barrier": "+0.1",
                                    "basis": "payout",
                                    "contract_type": "CALL",
                                    "currency": "USD",
                                    "duration": duration,
                                    "duration_unit": "s",
                                    "symbol": symbol,
                                }
                            )
                            if (
                                "error" not in call_proposal
                                and "proposal" in call_proposal
                            ):
                                logging.info(
                                    f"Possible buy: {threshold * (last_price - price)}"
                                )
                                # Buy if momentum is greater than threshold
                                if momentum >= threshold * (last_price - price):
                                    # Place buy order
                                    logging.info(f"Buy at {price}")
                                    await buy_proposal(api, call_proposal, price)

                        # Check if momentum is negative
                        elif momentum < 0:
                            put_proposal = await api.proposal(
                                {
                                    "proposal": proposal_amount,
                                    "amount": amount,
                                    "barrier": "-0.1",
                                    "basis": "payout",
                                    "contract_type": "PUT",
                                    "currency": "USD",
                                    "duration": duration,
                                    "duration_unit": "s",
                                    "symbol": symbol,
                                }
                            )
                            if (
                                "error" not in put_proposal
                                and "proposal" in put_proposal
                            ):
                                logging.info(
                                    f"Possible sell: {threshold * (last_price - price)}"
                                )
                                # Sell if momentum is less than threshold
                                if abs(momentum) >= threshold * (price - last_price):
                                    # Place sell order
                                    logging.info(f"Sell at {price}")
                                    await buy_proposal(api, put_proposal, price)

                # Update previous and last price
                prev_price = last_price
                last_price = price
                time.sleep(1)
                print(last_time, curr_time)
                print(prev_price, last_price)
            else:
                logging.info("Current algorithm, is ")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--symbol", default="R_100")
    parser.add_argument("-p", "--proposal", default=1, type=int)
    parser.add_argument("-a", "--amount", default=2, type=int)
    parser.add_argument("-d", "--duration", default=120, type=int)
    args = parser.parse_args()
    asyncio.run(main(args.symbol, args.proposal, args.amount, args.duration))
