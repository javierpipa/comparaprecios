
import os
from django.shortcuts import render
from django.conf import settings
from django.core.mail import EmailMultiAlternatives,send_mail, EmailMessage
from django.template.loader import get_template
from members.models import   Account
from django.db.models import Count, Sum, ExpressionWrapper, F, DurationField,  FloatField
# from .bi_functions import get_valores_de_ambientes
# from .views  import get_open_orders
from decimal import ROUND_DOWN, Decimal, getcontext

# For PDF
from django.template.loader import render_to_string
import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate,Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.views.decorators.cache import (
    cache_page, 
    never_cache, 
)
###



def send_email_account_daily(request,account_id, date,tests=False):
    
    print('send_email_account_daily:  ',  account_id)
    account= Account.objects.get(id=account_id)

    # pdf_file_name = create_dayly_pdf(account_id, date)
    # if tests:
    #     msg = EmailMessage("Day report for " + account.user.first_name + ' ' + account.user.last_name, "Content in PDF file", to=["javier.ignacio.pi.paredes@gmail.com"])
    # else:
    #     msg = EmailMessage("Day report for " + account.user.first_name + ' ' + account.user.last_name, "Content in PDF file", to=[account.user.email])
    # pdf_file_name_path = os.path.join(settings.MEDIA_ROOT, pdf_file_name )
    # msg.attach_file(pdf_file_name_path)
    msg.content_subtype = "html"
    msg.send()
    return pdf_file_name

    

# def send_week_email(request,account_id):
#     valor_btc_en_usd, variables_ambiente = get_valores_de_ambientes()
#     template_name = 'admin_binance/email/email_account_details.html'
#     print('send_mail_test:  ',  account_id)
#     account= Account.objects.get(id=account_id)

#     orders_by_type  = JPIOrder.objects.filter(jpi_order_account=account_id).values('type','status','side').annotate(total=Count('jpi_order_id')).order_by('type')
#     orders_by_date  = JPIOrder.objects.filter(jpi_order_account=account_id).values('timestamp__date').annotate(count=Count('jpi_order_id')).values('timestamp__date', 'count').order_by('timestamp__date')
#     open_orders  = JPIOrder.objects.filter(jpi_order_account=account_id, status='new').order_by('timestamp')

#     sell_orders_summary_btc = JPIOrder.objects.filter(jpi_order_account=account_id,side='sell',status='closed').values('close_timestamp__date')\
#         .annotate(
#             count=Count('jpi_order_id'),
#             cuantity=Sum('quantity'),
#             cost=Sum(ExpressionWrapper(F('order_finnaly_price')  * F('quantity'),output_field=FloatField())),
#             sold=Sum(ExpressionWrapper(F('price')  * F('quantity'),output_field=FloatField())),
#             margin=Sum(ExpressionWrapper( (F('price') * F('quantity') ) - (F('order_finnaly_price') * F('quantity') ) ,output_field=FloatField())),
#             marginUSD=Sum(ExpressionWrapper( (F('price') * F('quantity') * valor_btc_en_usd) - (F('order_finnaly_price') * F('quantity') * valor_btc_en_usd) ,output_field=FloatField())),
#         ).values('close_timestamp__date', 'cuantity','count', 'cost','sold', 'margin','marginUSD').order_by('close_timestamp__date')

#     sell_orders_total_btc = JPIOrder.objects.filter(jpi_order_account=account_id,side='sell',status='closed')\
#         .aggregate(
#             ordenes=Count('jpi_order_id'),cuanti=Sum('quantity'),
#             cost=Sum(ExpressionWrapper(F('order_finnaly_price')  * F('quantity'),output_field=FloatField())),
#             sold=Sum(ExpressionWrapper(F('price')  * F('quantity'),output_field=FloatField())),
#             margin=Sum(ExpressionWrapper( (F('price') * F('quantity') ) - (F('order_finnaly_price') * F('quantity') ) ,output_field=FloatField())),
#             marginUSD=Sum(ExpressionWrapper( (F('price') * F('quantity') * valor_btc_en_usd) - (F('order_finnaly_price') * F('quantity') * valor_btc_en_usd) ,output_field=FloatField())),
#         )

#     context = {
#         "account": account,
#         "orders_by_type": orders_by_type,
#         "open_orders": open_orders,
#         "orders_by_date": orders_by_date,
#         "sell_orders_summary_btc": sell_orders_summary_btc,
#         "sell_orders_total_btc": sell_orders_total_btc,
#     }
    
#     html_body = render_to_string( template_name, {'context': context})
#     send_mail(
#         'Week report',
#         'Here is the message.',
#         'javier.ignacio.pi.paredes@gmail.com',
#         [account.user.email],
#         html_message=html_body,
#         fail_silently=False,
#     )


# # 
    


# def create_dayly_pdf(account_id, date):
#     valor_btc_en_usd, variables_ambiente = get_valores_de_ambientes()
#     buffer = io.BytesIO()
#     styleSheet = getSampleStyleSheet()
#     pdf_file_name = 'account_'+str(account_id)+'_'+str(date)+'.pdf'
#     account = Account.objects.get(id=account_id)
#     doc = SimpleDocTemplate('media/'+pdf_file_name, pagesize = (595.27,400.00), rightMargin=5, leftMargin=5, topMargin=10, bottomMargin=0)
#     story=[]

#     ### Variables 
#     titles_font_size  = 6
#     data_font_size  = 7
#     from datetime import datetime, timezone
#     now = datetime.now()
#     now.strftime("%H:%M:%S")
#     account_user = account.user.first_name + ' ' + account.user.last_name 
#     account_member_from = account.user.date_joined.strftime("%d/%m/%Y")
    

#     account_days_member_delta_days = (datetime.now(timezone.utc) - account.user.date_joined).days
#     account_days_member_delta_month = Decimal(account_days_member_delta_days  / 30)
#     account_capital_invested = account.totalusd
#     account_capital_invested_btc = account.totalbtc
#     account_asset_free_to_trade = account.asset_free_to_trade
#     account_updated_capital_usd =  account.updated_capital_usd
#     ###
#     account_min_order_value_usd = account.min_order_value_usd
#     account_max_order_value_usd = account.max_order_value_usd
#     account_utility_per_order = account.utility_per_order
#     account_start_percentage = account.start_percentage
#     account_soft_close_orders = account.soft_close_orders 
#     if account_soft_close_orders: 
#         account_soft_close_orders = 'Enabled'
#     else:
#         account_soft_close_orders = 'Disabled'
#     account_soft_close_orders_max_loose_percent = account.soft_close_orders_max_loose_percent

#     ## Orders
#     open_orders = JPIOrder.objects.select_related('market').filter(jpi_order_account=account_id, status='new').order_by('timestamp')

#     ### Prepared data
#     fname = '<font size=8>' + account_user + ' <br/> the ' + date.strftime("%d/%m/%Y") + '<br/>' + now.strftime("%H:%M:%S") + '</font></para>'
    
    
#     #TABLA 1  ## Header
    
#     tipoDoc = Paragraph ('''<para align=LEFT><b>MyBinance<br/>Daily Report</b></para>''', styleSheet["BodyText"])
#     user = Paragraph('''<para align=RIGHT><font size=8>Details information for</font><br/>%s'''%fname, styleSheet["BodyText"])
   
#     tabla1 = Table([[tipoDoc, user]], colWidths=[200,290], rowHeights=None)
#     tabla1.setStyle([
#         ('VALIGN', (1,0), (2,0), 'TOP'),
#         ('ALIGN', (2,0), (2,0), 'RIGHT')#ALINEAR A LA DERECHA
#         ])
    
#     story.append(tabla1) #Construye la tabla 't' definida anteriormente
#     story.append(Spacer(0,10)) #Espacio del salto de línea con el siguiente Ejemplo

#     #Tabla usuario
#     story.append(Paragraph('''<para align=center><u>Account</u></para>''', styleSheet["BodyText"]))
#     data = []
#     data.append(["Name", "Member from", "Days member", "Month member", "Capital Invested BTC", "Capital Invested USD" , "Capital Updated USD"])
#     data.append([account_user, account_member_from, account_days_member_delta_days, format(account_days_member_delta_month,'.2f'), format(account_capital_invested_btc, ',.8f'), format(account_capital_invested, ',.2f'), format(account_updated_capital_usd, ',.2f')])

#     tabla = Table(data, colWidths=[2.7 * cm, 1.9 * cm, 2.0 * cm, 2.0 * cm, 2.7 * cm, 2.7 * cm, 2.3 * cm])

#     tabla.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (5, 0), data_font_size),
#         ### third row
#         ('FONTSIZE', (0, 2), (5, 2), titles_font_size),
        
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (6,-1), 'RIGHT'),#Centrar renta #1

#     ]))

#     story.append(Spacer(3,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla) #Construye la tabla 't' definida anteriormente

#     # Segunda linea
#     data = []
#     story.append(Paragraph('''<para align=center><u>Orders Settings</u></para>''', styleSheet["BodyText"]))
#     data.append(["Min.Order USD", "Max.Order USD", "Utility % per order", "% to trade", "Soft Order Close", "Max.Loose %","Max.Loose USD" ])
#     data.append([format(account_min_order_value_usd,',.2f'), format(account_max_order_value_usd,',.2f'), account_utility_per_order, format(account_start_percentage,'.2f'), account_soft_close_orders, format(account_soft_close_orders_max_loose_percent,'.4f'), format(account.soft_close_orders_max_loose_usd,',.2f')])
#     tabla = Table(data, colWidths=[2.1 * cm, 2.1 * cm, 2.2 * cm, 1.6 * cm, 2.2 * cm, 1.9 * cm, 4.1 * cm])
#     tabla.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (6, 0), data_font_size),
#         ### third row
#         ('FONTSIZE', (0, 2), (6, 2), titles_font_size),
        
#         ### ultimas 4 columnas
#         ('ALIGN', (0,1), (6,-1), 'RIGHT'),#Centrar renta #1
#         ### Last Row
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))
#     story.append(Spacer(3,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla) #Construye la tabla 't' definida anteriormente

#     #TABLA 3 # Balance
#     # Total de ordenes cerradas y abiertas
#     story.append(Paragraph('''<para align=center><u>Sale Orders Closed in USD</u></para>''', styleSheet["BodyText"]))
#     data3 = []
#     data3.append(["# Orders", "Cost", "Avg.Cost", "Capital Rotation",  "Sales",  "Utility(1)",  "Utility %",  "Utility %/month","Capital+Utility" ])
#     # sell_orders_total_btc = JPIOrder.objects.filter(jpi_order_account=account_id,side='sell', status='closed')\
#     #     .aggregate(
#     #         ordenes=Count('jpi_order_id'),
#     #         cost=Sum(ExpressionWrapper(F('order_finnaly_price')
#     #                  * F('quantity'), output_field=FloatField())),
#     #         sold=Sum(ExpressionWrapper(F('price') *
#     #                  F('quantity'), output_field=FloatField())),
#     #         margin=Sum(ExpressionWrapper((F('price') * F('quantity')) -
#     #                    (F('order_finnaly_price') * F('quantity')), output_field=FloatField())),
#     #         marginUSD=Sum(ExpressionWrapper((F('price') * F('quantity') * valor_btc_en_usd) - (
#     #             F('order_finnaly_price') * F('quantity') * valor_btc_en_usd), output_field=FloatField())),
#     # )
#     sell_orders_total_btc = Account.order_sell_closed(account_id)
#     closed_tot_ordenes        = sell_orders_total_btc['ordenes']
#     if closed_tot_ordenes == 0:
#         closed_tot_ordenes = 1

#     closed_tot_cost_usd       = Decimal(sell_orders_total_btc['cost'] * valor_btc_en_usd)
#     closed_avg_cost_usd       = closed_tot_cost_usd / closed_tot_ordenes
#     capital_rotation          = closed_tot_cost_usd  / account_capital_invested  
#     closed_tot_sold           = sell_orders_total_btc['sold'] * valor_btc_en_usd
#     closed_tot_margin         = sell_orders_total_btc['margin']
#     win_usd                   = Decimal(sell_orders_total_btc['marginUSD'])
#     win_percent               = (win_usd  / account_capital_invested) 
#     win_percent_per_month     = win_percent / account_days_member_delta_month
#     capital_plus_wins         = win_usd + account_capital_invested
#     data3.append([
#         closed_tot_ordenes, 
#         format(closed_tot_cost_usd, ',.2f'), 
#         format(closed_avg_cost_usd, ',.2f'), 
#         format(capital_rotation,'.1f'), 
#         format(closed_tot_sold, ',.2f'), 
#         format(win_usd, ',.2f'), 
#         format(win_percent,'.2%'), 
#         format(win_percent_per_month,'.2%'), 
#         format(capital_plus_wins, ',.2f')])

    
#     tabla3 = Table(data3, colWidths=[1.7* cm, 1.5 * cm, 1.6 * cm, 2.4 * cm, 1.6 * cm, 1.6 * cm, 1.5 * cm, 2.1 * cm, 2.2 * cm])
#     tabla3.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (8, 0), data_font_size),
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (8,-1), 'RIGHT'),#Centrar renta #1
#         ### Before Last Row
#         # ('SPAN',(0,-2),(3,-2)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-2), (-1,-2), 8), #Tamaño de la Resolucion
#         # ### Last Row
#         # ('SPAN',(0,-1),(3,-1)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))

#     #Constructor y espaciado
#     story.append(Spacer(0,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla3) #Construye la tabla 't' definida anteriormente

#     #TABLA 4# Pending Orders Details
#     story.append(Paragraph('''<para align=center><u>Pending Orders Details in USD</u></para>''', styleSheet["BodyText"]))
#     data4 = []
#     data4.append([ "Order Date", "Days delta", "Market", "Price ", "Last Price", "Margin %"])
    
#     # open_orders_by_date = get_open_orders(account_id)
#     for uno in open_orders:
#         price  =  Decimal(uno.price *  uno.quantity)  * Decimal(valor_btc_en_usd)
#         lastprice  = uno.last_price  * uno.quantity * Decimal(valor_btc_en_usd)
        
#         data4.append([
#             uno.timestamp.strftime("%d-%m, %H:%M"),                                      #1
#             uno.time_from_created,                              #2
#             uno.market,                                         #3
#             format(price,',.2f'),                               #4
#             format(lastprice, ',.2f'),                          #5
#             format(uno.price_difference_percentage,'.2f')+' %',      #6

#         ])
#     tabla4 = Table(data4, colWidths=[2.8* cm, 1.8* cm, 1.7* cm, 1.5 * cm, 1.4 * cm, 1.4 * cm,  2.0 * cm,  1.8 * cm,  1.8 * cm,  2.1 * cm])
#     tabla4.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (9, 0), data_font_size),
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (10,-1), 'RIGHT'),#Centrar renta #1
#         ### Before Last Row
#         # ('SPAN',(0,-2),(3,-2)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-2), (-1,-2), 8), #Tamaño de la Resolucion
#         # ### Last Row
#         # ('SPAN',(0,-1),(3,-1)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))
#     story.append(Spacer(0,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla4) #Construye la tabla 't' definida anteriormente


#     #TABLA 4.1# Pending Orders
#     story.append(Paragraph('''<para align=center><u>Pending Orders in USD</u></para>''', styleSheet["BodyText"]))
#     data4 = []
#     data4.append([ "# Orders", "Cost", "Investment %", "Upd.Cost", "Loose(2)", "Loose %","Pend.Utility(1-2)", "Exp.Sell Value","Exp.Utility(3)", "Total Utility(1+3)" ])
#     open_orders_totals = JPIOrder.objects.select_related('market').filter(jpi_order_account=account_id,status='new')\
#         .aggregate(
#             ordenes=Count('jpi_order_id'),
#             order_cost=Sum(ExpressionWrapper(
#                 F('order_finnaly_price') * F('quantity'), output_field=FloatField())),
#             last_order_cost=Sum(ExpressionWrapper(
#                 F('market__close_price_one_hour') * F('quantity'), output_field=FloatField())),
#             order_sell=Sum(ExpressionWrapper(
#                 F('price') * F('quantity'), output_field=FloatField())),
            
#             marginUSD=Sum(ExpressionWrapper((F('market__close_price_one_hour') * F('quantity') * valor_btc_en_usd) -
#                           (F('order_finnaly_price') * F('quantity') * valor_btc_en_usd), output_field=FloatField())),
#     )
#     if open_orders_totals['order_cost'] is None:
#         open_orders_totals['order_cost'] = 0
#         open_orders_totals['last_order_cost'] = 0
#         open_orders_totals['margin'] = 0
#         open_orders_totals['order_cost_USD'] = 0
#         open_orders_totals['last_order_cost_USD'] = 0
#         open_orders_totals['marginUSD'] = 0
#         open_orders_totals['ordenes'] = 1
#         open_orders_totals['order_sell'] = 0
        
        
#     # if closed_tot_ordenes == 0:
#     pending_tot_ordenes        = open_orders_totals['ordenes']
#     pending_tot_cost           = Decimal(open_orders_totals['order_cost']  * valor_btc_en_usd)
#     inverted_percent           = (pending_tot_cost / capital_plus_wins)
#     pending_tot_sold           = Decimal(open_orders_totals['last_order_cost'] * valor_btc_en_usd)
#     pending_looseUSD           = Decimal(open_orders_totals['marginUSD'])
#     pending_loose_percent      = pending_looseUSD / capital_plus_wins
#     win_less_loose             = (win_usd + pending_looseUSD)
#     pending_tot_order_sell     = Decimal(open_orders_totals['order_sell']) * Decimal(valor_btc_en_usd)
    
#     future_profit_usd          = (pending_tot_order_sell- pending_tot_cost)
#     total_utility              = future_profit_usd +  win_usd
    
#     # win_less_loose_percent     = win_less_loose /  capital_plus_wins
#     data4.append([
#         pending_tot_ordenes,                    #1
#         format(pending_tot_cost,',.2f'),        #2
#         format(inverted_percent,'.2%'),         #3
#         format(pending_tot_sold,',.2f'),        #4
#         format(pending_looseUSD, ',.2f'),       #5
#         format(pending_loose_percent,'.2%'),    #6
#         format(win_less_loose, ',.2f'),         #7
#         format(pending_tot_order_sell, ',.2f'), #8
#         format(future_profit_usd,',.2f'),       #9
#         format(total_utility,',.2f'),           #10
#         ])

#     ###                               1         2         3         4         5         6         7         8         9         10 
#     tabla4 = Table(data4, colWidths=[1.3* cm, 1.2* cm, 1.7* cm, 1.5 * cm, 1.4 * cm, 1.4 * cm,  2.0 * cm,  1.8 * cm,  1.8 * cm,  2.1 * cm])
#     tabla4.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (9, 0), data_font_size),
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (10,-1), 'RIGHT'),#Centrar renta #1
#         ### Before Last Row
#         # ('SPAN',(0,-2),(3,-2)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-2), (-1,-2), 8), #Tamaño de la Resolucion
#         # ### Last Row
#         # ('SPAN',(0,-1),(3,-1)), #Combinar filas final y penultima
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))
#     story.append(Spacer(0,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla4) #Construye la tabla 't' definida anteriormente


#      #TABLA 2 # Closed orders this date
#     closed_orders   = JPIOrder.objects.filter(jpi_order_account=account_id,close_timestamp__date=date,side='sell',status='closed')

#     story.append(Paragraph('''<para align=center><u>Closed orders this date </u></para>''', styleSheet["BodyText"]))
#     data = []
#     data.append(["Market", "Created (Date-Hour)", "Cost BTC", "Sold BTC", "Profit BTC", "Profit USD i)" ])
#     marginBTC_total = 0
#     marginUSD_total = 0
#     for order in closed_orders:
#         opened      = order.timestamp.strftime("%b %d, %Y - %H:%M")
#         cost        = format(order.order_finnaly_price * order.quantity, '.8f')
#         sold        = format(order.price * order.quantity, '.8f')
#         marginBTC   = (order.price * order.quantity) - (order.order_finnaly_price * order.quantity)
#         marginUSD1  = float(order.price * order.quantity) * valor_btc_en_usd
#         marginUSD2  = float(order.order_finnaly_price * order.quantity) * valor_btc_en_usd
#         marginUSD   = marginUSD1 - marginUSD2
#         # delta = timedelta.Timedelta(order.close_timestamp - order.timestamp)

#         marginBTC_total += marginBTC
#         marginUSD_total += marginUSD
#         data.append([order.market, opened, cost, sold, format(marginBTC, '.8f'), format(marginUSD, '.2f')])

#     data.append(['Total', '', '', '', format(marginBTC_total, '.8f'), format(marginUSD_total, '.2f')])
    
#     tabla2 = Table(data, colWidths=[3.5 * cm, 3.2 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.1 * cm])
#     tabla2.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (5, 0), data_font_size),
        
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (5,-1), 'RIGHT'),#Centrar renta #1
#         ### Last Row
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))

#     # Espaciado
#     story.append(Spacer(3,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     story.append(tabla2) #Construye la tabla 't' definida anteriormente
    
    
#     #TABLA 5# Orders created today
#     story.append(Paragraph('''<para align=center><u>Orders created today</u></para>''', styleSheet["BodyText"]))
#     story.append(Spacer(0,10)) #Espacio del salto de línea con el siguiente Ejemplo
#     data5 = []
#     data5.append(['Item','Cuantity','Cost','Sell Price','Total BTC','Total USD'])
#     orders_created_today = JPIOrder.objects.filter(jpi_order_account=account_id,timestamp__date=date,side='sell',status='closed')\
#         .aggregate(
#             ordenes=Count('jpi_order_id'),
#             order_cost=Sum(ExpressionWrapper(
#                 F('order_finnaly_price') * F('quantity'), output_field=FloatField())),
#             last_order_cost=Sum(ExpressionWrapper(
#                 F('market__close_price_one_hour') * F('quantity'), output_field=FloatField())),
#             margin=Sum(ExpressionWrapper((F('market__close_price_one_hour') * F('quantity')) -
#                           (F('order_finnaly_price') * F('quantity')), output_field=FloatField())),
#             marginUSD=Sum(ExpressionWrapper((F('market__close_price_one_hour') * F('quantity') * valor_btc_en_usd) -
#                             (F('order_finnaly_price') * F('quantity') * valor_btc_en_usd), output_field=FloatField())),
#     )
#     if orders_created_today['ordenes'] == 0:
#         data5.append(['No orders created today'])
#     else:
#         orders_created_today_ordenes        = orders_created_today['ordenes']
#         orders_created_today_cost           = orders_created_today['order_cost']
#         orders_created_today_sold           = orders_created_today['last_order_cost']
#         orders_created_today_margin         = orders_created_today['margin']
#         orders_created_today_marginUSD      = orders_created_today['marginUSD']
#         data5.append(['New Orders',orders_created_today_ordenes, orders_created_today_cost, orders_created_today_sold, format(orders_created_today_margin, '.8f'), format(orders_created_today_marginUSD, '.2f')])
    
#     tabla5 = Table(data5, colWidths=[3 * cm, 3.2 * cm, 2.5 * cm, 2.5 * cm])
#     tabla5.setStyle(TableStyle([
#         ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
#         ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
#         ('FONTSIZE', (0, 0), (-1, -1), titles_font_size), #Tamaño de la Resolucion
#         ### first row
#         ('FONTSIZE', (0, 0), (5, 0), data_font_size),
#         ### ultimas 4 columnas
#         ('ALIGN', (1,1), (5,-1), 'RIGHT'),#Centrar renta #1
#         ### Before Last Row
        
#         # ('FONTSIZE', (0,-2), (-1,-2), 8), #Tamaño de la Resolucion
#         # ### Last Row
        
#         # ('FONTSIZE', (0,-1), (-1,-1), 8), #Tamaño de la Resolucion
#         # ('TEXTCOLOR',(0,-1), (-1,-1),colors.black),
#     ]))

#     story.append(tabla5) #Construye la tabla


#     #TABLA 6# Notas
#     story.append(Spacer(5,2)) #Espacio del salto de línea con el siguiente Ejemplo
    
#     header = Paragraph('''<para align=left>Notes:</para>''', styleSheet["BodyText"])
#     value1 =  format(valor_btc_en_usd, ',.2f') + '  </i>  </b></font></para>'
#     nota1 = Paragraph('''<para align=justify><font size=8>i)<b><i><u> BTC  value in USD:</u> %s'''%value1, styleSheet["BodyText"])
   
#     tabla6 = Table(
#         [
#             [header],
#             [nota1]
#         ]
#         , colWidths=[490]
#         , rowHeights=None)
#     tabla5.setStyle([
#         ('VALIGN', (1,0), (2,0), 'TOP'),
#         ('ALIGN', (2,0), (2,0), 'LEFT')
#         ])
    
#     story.append(tabla6) #Construye la tabla 't' definida anteriormente


#     doc.build(story) #Constructor del documento
    
#     pdf = buffer.getvalue()
#     buffer.close()

#     return(pdf_file_name)
#     # return(pdf)
#     # buffer = io.BytesIO()
#     # return FileResponse(buffer, as_attachment=True, filename='media/2factura_auto_inquilino.pdf')




# def otros():
#     # d = Context({ 'username': account.user.first_name })

#     # htmly     = get_template(template_name)
#     # html_body = render(context)
#     # message = EmailMultiAlternatives(
#     #    subject='Django HTML Email',
#     #    body="mail testing",
#     #    from_email='xyz@abc.com',
#     #    to=['javier.ignacio.pi.paredes@gmail.com']
#     # )
#     # message.attach_alternative(html_body, "text/html")
#     # message.send(fail_silently=False)


#     # return  context
#     # plaintext = get_template('email.txt')
#     # plaintext = get_template(template_name)
#     # htmly     = get_template(template_name)

#     # # d = Context({ 'username': username })

#     # subject, from_email, to = 'hello', 'from@example.com', 'javier.ignacio.pi.paredes@gmail.com'
#     # # text_content = plaintext.render(context)
#     # html_content = htmly.render(context)
#     # msg = EmailMultiAlternatives(subject, "hola", from_email, [to])
#     # msg.attach_alternative(html_content, "text/html")
#     # msg.send()

#     return  "data"