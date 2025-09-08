# Forex Signals Web (TradingView)

واجهة Flask تسحب بيانات مباشرة من TradingView باستخدام مكتبة tvDatafeed.
تعرض إشارات CALL/PUT مبنية على RSI + EMA + MACD.

## التشغيل محليًا
```bash
pip install -r requirements.txt
python web_signals_tv.py
```
- تأكد من تعديل username/password لحساب TradingView.

## التشغيل على Railway
1. ارفع الملفات على GitHub (web_signals_tv.py, requirements.txt, Procfile, README.md).
2. في Railway: New Project → Deploy from GitHub.
3. في Settings → Start Command:
   ```
   gunicorn web_signals_tv:app --bind 0.0.0.0:$PORT --workers 1
   ```
4. اعمل Deploy وخد الرابط العام.