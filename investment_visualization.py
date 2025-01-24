def simulate_investment_data():
    days = 365
    poisson_rate = 0.15
    total_investment = 0
    portfolio = defaultdict(dict)
    history = []

    # Helper function to create an investor
    def create_investor(day):
        investment = np.random.uniform(investmentRange["min"], investmentRange["max"])
        lock_period = lockPeriods[0] if np.random.random() < 0.5 else lockPeriods[1]  # 6 or 12 months
        return {
            "investment": investment,
            "entryDay": day,
            "lockPeriod": lock_period,
            "isActive": True
        }

    # Initial investors
    for i in range(5):
        investor_id = f"Investor_{i+1}"
        portfolio[investor_id] = create_investor(0)
        total_investment += portfolio[investor_id]["investment"]

    # Simulate days
    for day in range(days):
        # Process exits
        for investor_id, investor in portfolio.items():
            if not investor["isActive"]:
                continue

            # Check for early withdrawal
            if np.random.random() < earlyWithdrawalPenalty / 365:  # Daily probability
                investor["isActive"] = False
                total_investment -= investor["investment"] * (1 - earlyWithdrawalPenalty)

            # Check for lock period expiry
            elif day - investor["entryDay"] >= investor["lockPeriod"]:
                if np.random.random() < 0.3:  # 30% chance to exit after lock period
                    investor["isActive"] = False
                    total_investment -= investor["investment"]

        # Deduct management fee
        total_investment -= total_investment * managementFee / 365

        # New investors (Poisson distribution)
        num_new_investors = 1 if np.random.random() < poisson_rate else 0

        for _ in range(num_new_investors):
            investor_id = f"Investor_{len(portfolio) + 1}"
            new_investor = create_investor(day)
            portfolio[investor_id] = new_investor
            total_investment += new_investor["investment"]

        # Calculate percentages and create daily snapshot
        day_data = {
            "day": day,
            "totalInvestment": total_investment,
            "numInvestors": sum(1 for inv in portfolio.values() if inv["isActive"]),
            "activeInvestors": 0,
            "percentages": {}
        }

        for investor_id, investor in portfolio.items():
            if investor["isActive"]:
                day_data[f"{investor_id}_pct"] = (investor["investment"] / total_investment) * 100
                day_data["activeInvestors"] += 1
            else:
                day_data[f"{investor_id}_pct"] = 0

        history.append(day_data)

    return pd.DataFrame(history)
