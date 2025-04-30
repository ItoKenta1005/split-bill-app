from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def settle():
    results = []
    people = []
    score_profits = []
    total_paid = 0
    total_adjusted = 0
    rate = 0.1
    error = None

    if request.method == 'POST':
        try:
            rate = float(request.form.get('rate', 0.1))
        except ValueError:
            rate = 0.1

        names = [request.form.get(f'name{i}') for i in range(1, 5)]
        pays = []
        scores = []

        for i in range(1, 5):
            try:
                pay = float(request.form.get(f'pay{i}', 0))
            except ValueError:
                pay = 0.0
            pays.append(pay)

            try:
                score = float(request.form.get(f'score{i}', 0))
            except ValueError:
                score = 0.0
            scores.append(score)

        # 成績損益の仮計算（常に必要）
        score_profits = [round(score * rate * 100, 2) for score in scores]
        adjusted = [round(p + s, 2) for p, s in zip(pays, score_profits)]

        # people は必ず保持（値復元のため）
        people = [{
            'name': n,
            'pay': p,
            'score': s,
            'profit': sp,
            'adjusted': a
        } for n, p, s, sp, a in zip(names, pays, scores, score_profits, adjusted)]

        # 成績合計チェック
        total_score = sum(scores)
        if abs(total_score) > 0.01:
            error = f"成績の合計が 0 ではありません（現在の合計：{round(total_score, 2)}）。成績の総和がゼロになるように調整してください。"
        else:
            total_paid = round(sum(pays), 2)
            total_adjusted = round(sum(adjusted), 2)
            avg = round(total_adjusted / 4, 2)

            balances = [{'name': p['name'], 'diff': round(p['adjusted'] - avg, 2)} for p in people]
            over = [p for p in balances if p['diff'] > 0]
            under = [p for p in balances if p['diff'] < 0]

            i = j = 0
            while i < len(over) and j < len(under):
                payer = under[j]
                receiver = over[i]
                amount = min(receiver['diff'], -payer['diff'])
                results.append(f"{payer['name']} → {receiver['name']} に {round(amount, 2)} 円")
                receiver['diff'] -= amount
                payer['diff'] += amount
                if abs(receiver['diff']) < 1e-2:
                    i += 1
                if abs(payer['diff']) < 1e-2:
                    j += 1

    return render_template(
        'settle.html',
        rate=rate,
        people=people,
        score_profits=score_profits,
        total_paid=total_paid,
        total_adjusted=total_adjusted,
        results=results,
        error=error
    )

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)