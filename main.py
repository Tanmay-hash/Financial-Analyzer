import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def colorize(value, good_threshold, bad_threshold, is_percent=False):
    """Colorize output based on thresholds"""
    if value == 'N/A':
        return Fore.WHITE + str(value)
    
    display_value = f"{value:.2f}%" if is_percent else f"{value:.2f}"
    
    if value >= good_threshold:
        return Fore.GREEN + display_value
    elif value <= bad_threshold:
        return Fore.RED + display_value
    return Fore.YELLOW + display_value

def analyze_company(ticker_symbol):
    """Analyze company financials and provide investment insights."""
    try:
        company = yf.Ticker(ticker_symbol)
        info = company.info
        
        print(f"\n{Fore.CYAN}=== Financial Analysis for {ticker_symbol} ==={Style.RESET_ALL}")
        print(f"Company Name: {info.get('longName', 'N/A')}")
        print(f"Industry: {info.get('industry', 'N/A')}")
        print(f"Sector: {info.get('sector', 'N/A')}\n")

        # Current price and valuation
        current_price = info.get('currentPrice', 'N/A')
        previous_close = info.get('previousClose', 'N/A')
        price_change = ((current_price - previous_close) / previous_close * 100 
                       if all(isinstance(x, (int, float)) for x in [current_price, previous_close]) 
                       else 'N/A')
        
        print(f"{Fore.WHITE}Current Price:{Style.RESET_ALL} ${current_price}")
        if price_change != 'N/A':
            change_color = Fore.GREEN if price_change >= 0 else Fore.RED
            print(f"Price Change: {change_color}{price_change:.2f}%{Style.RESET_ALL} (from prev close)")
        
        print(f"Market Cap: ${info.get('marketCap', 'N/A'):,.2f}")
        print(f"52-Week Range: {info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}")

        # Valuation metrics
        print(f"\n{Fore.WHITE}Valuation:{Style.RESET_ALL}")
        pe = info.get('trailingPE', 'N/A')
        peg = info.get('pegRatio', 'N/A')
        ps = info.get('priceToSalesTrailing12Months', 'N/A')
        
        print(f"P/E Ratio: {colorize(pe, 15, 25) if pe != 'N/A' else 'N/A'}")
        print(f"PEG Ratio: {colorize(peg, 1, 2) if peg != 'N/A' else 'N/A'}")
        print(f"P/S Ratio: {colorize(ps, 2, 5) if ps != 'N/A' else 'N/A'}")
        print(f"Forward P/E: {info.get('forwardPE', 'N/A')}")

        # Profitability
        print(f"\n{Fore.WHITE}Profitability:{Style.RESET_ALL}")
        roe = info.get('returnOnEquity', 'N/A')
        pm = info.get('profitMargins', 'N/A')
        rev_growth = info.get('revenueGrowth', 'N/A')
        
        print(f"Return on Equity: {colorize(roe*100, 15, 5, True) if roe != 'N/A' else 'N/A'}")
        print(f"Profit Margin: {colorize(pm*100, 10, 5, True) if pm != 'N/A' else 'N/A'}")
        print(f"Revenue Growth: {colorize(rev_growth*100, 10, 0, True) if rev_growth != 'N/A' else 'N/A'}")

        # Financial Health
        print(f"\n{Fore.WHITE}Financial Health:{Style.RESET_ALL}")
        dte = info.get('debtToEquity', 'N/A')
        cr = info.get('currentRatio', 'N/A')
        fcf = info.get('freeCashflow', 'N/A')
        
        print(f"Debt to Equity: {colorize(dte, 0.5, 1.5) if dte != 'N/A' else 'N/A'}")
        print(f"Current Ratio: {colorize(cr, 1.5, 1.0) if cr != 'N/A' else 'N/A'}")
        print(f"Free Cash Flow: ${fcf/1e9:,.2f}B" if fcf != 'N/A' else "Free Cash Flow: N/A")

        # Dividend information
        if info.get('dividendYield'):
            print(f"\n{Fore.WHITE}Dividend Info:{Style.RESET_ALL}")
            print(f"Dividend Yield: {colorize(info['dividendYield']*100, 3, 1, True)}")
            print(f"Payout Ratio: {info.get('payoutRatio', 'N/A')}")
            print(f"Dividend Growth (5Y): {info.get('fiveYearAvgDividendGrowthRate', 'N/A')}")

        # Analyst ratings
        print(f"\n{Fore.WHITE}Analyst Ratings:{Style.RESET_ALL}")
        print(f"Recommendation: {info.get('recommendationKey', 'N/A').title()}")
        print(f"Mean Target: ${info.get('targetMeanPrice', 'N/A')}")
        print(f"High Target: ${info.get('targetHighPrice', 'N/A')}")
        print(f"Low Target: ${info.get('targetLowPrice', 'N/A')}")

        # Generate investment score
        score = 0
        reasons = []
        warning = []

        # Positive factors
        if isinstance(info.get('recommendationMean'), float) and info['recommendationMean'] < 2.5:
            score += 1
            reasons.append("Positive analyst recommendations")
        if isinstance(roe, float) and roe > 0.15:
            score += 1
            reasons.append("Strong return on equity")
        if isinstance(dte, float) and dte < 0.5:
            score += 2  # Extra weight for low debt
            reasons.append("Low debt levels")
        elif isinstance(dte, float) and dte < 1.0:
            score += 1
            reasons.append("Moderate debt levels")
        if isinstance(pm, float) and pm > 0.1:
            score += 1
            reasons.append("Good profit margins")
        if isinstance(rev_growth, float) and rev_growth > 0.1:
            score += 1
            reasons.append("Strong revenue growth")

        # Warning signs
        if isinstance(dte, float) and dte > 1.5:
            warning.append("High debt levels")
        if isinstance(cr, float) and cr < 1.0:
            warning.append("Potential liquidity issues")
        if isinstance(pe, float) and pe > 25:
            warning.append("High valuation (P/E)")
        if isinstance(peg, float) and peg > 2:
            warning.append("High growth-adjusted valuation (PEG)")

        # Print investment summary
        print(f"\n{Fore.WHITE}Investment Summary:{Style.RESET_ALL}")
        if score >= 5:
            print(f"{Fore.GREEN}✅ STRONG: This company shows excellent financial indicators")
        elif score >= 3:
            print(f"{Fore.GREEN}🟢 GOOD: This company shows positive financial indicators")
        elif score >= 1:
            print(f"{Fore.YELLOW}🟡 CAUTION: This company shows mixed financial indicators")
        else:
            print(f"{Fore.RED}🔴 WEAK: This company shows concerning financial indicators")

        if reasons:
            print(f"\n{Fore.GREEN}Strengths:")
            for reason in reasons:
                print(f"• {reason}")

        if warning:
            print(f"\n{Fore.RED}Risks:")
            for warn in warning:
                print(f"• {warn}")

        print(f"\n{Fore.YELLOW}Note: This is automated analysis only. Always do further research before investing.")

    except Exception as e:
        print(f"{Fore.RED}Error analyzing {ticker_symbol}: {str(e)}")

def main():
    print(f"{Fore.CYAN}\nWelcome to the Enhanced Financial Analyzer!")
    print("This tool helps you analyze companies for potential investment.")
    print("Enter stock tickers like 'AAPL' for Apple or 'MSFT' for Microsoft")
    print("Type 'quit' to exit\n")
    
    while True:
        ticker = input(f"{Fore.WHITE}Enter company ticker symbol: ").upper().strip()
        if ticker == 'QUIT':
            break
        analyze_company(ticker)

if __name__ == "__main__":
    main()
