from flask import Flask, render_template_string
from tvDatafeed import TvDatafeed, Interval
import ta

app = Flask(__name__)

# ===== تسجيل دخول في TradingView =====
# ⚠️ استبدل بريدك وكلمة السر لحساب TradingView
tv = TvDatafeed(username='بريدك', password='باسوردك')

# ===== الأزواج =====
pairs = {
    "EUR/USD": ("EURUSD", "OANDA"),
    "GBP/USD": ("GBPUSD", "OANDA"),
    "USD/JPY": ("USDJPY", "OANDA"),
    "USD/CHF": ("USDCHF", "OANDA"),
    "AUD/USD": ("AUDUSD", "OANDA"),
    "NZD/USD": ("NZDUSD", "OANDA"),
    "USD/CAD": ("USDCAD", "OANDA"),
    "EUR/GBP": ("EURGBP", "OANDA"),
    "EUR/JPY": ("EURJPY", "OANDA"),
    "GBP/JPY": ("GBPJPY", "OANDA"),
    "AUD/JPY": ("AUDJPY", "OANDA"),
    "EUR/AUD": ("EURAUD", "OANDA"),
    "EUR/CHF": ("EURCHF", "OANDA"),
    "GBP/CHF": ("GBPCHF", "OANDA"),
    "NZD/JPY": ("NZDJPY", "OANDA"),
    "CHF/JPY": ("CHFJPY", "OANDA"),
    "USD/TRY": ("USDTRY", "OANDA"),
    "USD/MXN": ("USDMXN", "OANDA"),
    "USD/ZAR": ("USDZAR", "OANDA"),
}

def analyze(symbol, exchange):
    try:
        df = tv.get_hist(symbol=symbol, exchange=exchange,
                         interval=Interval.in_1_minute, n_bars=200)
        if df is None or df.empty:
            return "NO_DATA", 0

        close = df['close']

        rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
        ema_fast = ta.trend.EMAIndicator(close, window=9).ema_indicator().iloc[-1]
        ema_slow = ta.trend.EMAIndicator(close, window=21).ema_indicator().iloc[-1]
        macd_ind = ta.trend.MACD(close)
        macd = macd_ind.macd().iloc[-1]
        macd_signal = macd_ind.macd_signal().iloc[-1]

        score = 0
        if rsi < 30: score += 1
        if rsi > 70: score -= 1
        if ema_fast > ema_slow: score += 1
        if ema_fast < ema_slow: score -= 1
        if macd > macd_signal: score += 1
        if macd < macd_signal: score -= 1

        if score >= 2: return "CALL", score
        elif score <= -2: return "PUT", score
        else: return "NO_TRADE", score
    except Exception:
        return "ERROR", 0

@app.route("/")
def index():
    results = []
    for name, (symbol, exch) in pairs.items():
        signal, score = analyze(symbol, exch)
        results.append((name, signal, score))

    results.sort(key=lambda x: abs(x[2]), reverse=True)
    best = results[0] if results else ("N/A", "N/A", 0)

    template = """
    <html>
    <head>
        <meta charset="utf-8">
        <title>إشارات الفوركس (TradingView)</title>
        <style>
            body { font-family: Arial; background:#0b0f14; color:#eee; text-align:center; }
            table { margin:auto; border-collapse: collapse; width:80%; }
            th, td { border:1px solid #555; padding:6px; }
            th { background:#222; }
            .CALL { color: #00ff88; font-weight:bold; }
            .PUT { color: #ff4444; font-weight:bold; }
            .NO_TRADE { color: #aaa; }
            .best { font-size: 1.4em; margin:20px; }
        </style>
    </head>
    <body>
        <h1>📊 إشارات الفوركس (TradingView + RSI + EMA + MACD)</h1>
        <div class="best">🔥 أفضل صفقة الآن: <b>{{best[0]}}</b> → 
        <span class="{{best[1]}}">{{best[1]}}</span> (Score {{best[2]}})</div>
        <table>
            <tr><th>الزوج</th><th>التوقع</th><th>Score</th></tr>
            {% for r in results %}
            <tr>
                <td>{{r[0]}}</td>
                <td class="{{r[1]}}">{{r[1]}}</td>
                <td>{{r[2]}}</td>
            </tr>
            {% endfor %}
        </table>
        <p>🔄 حدّث الصفحة لتشوف آخر الإشارات</p>
    </body>
    </html>
    """
    return render_template_string(template, results=results, best=best)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)