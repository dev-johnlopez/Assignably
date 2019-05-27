from app import app

@app.template_filter('currency')
def currency(value):
    return '${:,.2f}'.format(value)
