import datetime
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from sgt_App.models import Entries
from django.contrib.auth.decorators import login_required
from sgt_App import forms
import xlwt
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Sum


# Create your views here.
@login_required
def index_view(request):
    return render(request, 'index.html')


def logout_view(request):
    return render(request, "logout.html")


# Entry CRUD Operations---------------------------------------------------------
@login_required
def view_entry(request):
    entry = Entries.objects.order_by('-lr_no')
    paginator = Paginator(entry, 10)
    page = request.GET.get('page')
    sum = Entries.objects.aggregate(Sum('total_balance'))
    try:
        post = paginator.page(page)
    except PageNotAnInteger:
        post = paginator.page(1)
    except EmptyPage:
        post = paginator.page(paginator.num_pages)
    my_dict = {'entry': entry, 'post': post, 'page': page, 'total_sum': sum['total_balance__sum']}
    return render(request, 'list.html', context=my_dict)


@login_required
def add_entry(request):
    form = forms.AddEntryForm()
    if request.method == 'POST':
        form = forms.AddEntryForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            lr_no = form.cleaned_data['lr_no']
            vehicle_no = form.cleaned_data['vehicle_no'].strip()
            location = form.cleaned_data['location'].strip()
            amount = float(form.cleaned_data['amount'])
            cash = float(form.cleaned_data['cash'])
            diesel = float(form.cleaned_data['diesel'])
            rtgs = float(form.cleaned_data['rtgs'])
            commission = float(form.cleaned_data['commission'])
            status = form.cleaned_data['status']
            firm_name = form.cleaned_data['firm_name']
            total_balance = amount - (cash + diesel + rtgs + commission)
            Entries(date=date, firm_name=firm_name, lr_no=lr_no, vehicle_no=vehicle_no, location=location, amount=amount, cash=cash,
                    diesel=diesel, rtgs=rtgs,
                    commission=commission, status=status, total_balance=total_balance).save()
            messages.success(request, 'Your entry has been successfully Inserted')
            return HttpResponseRedirect('/view_entry')
    else:
        return render(request, 'add_entry1.html', {'form': form})


def entry_detail(request, lr_no):
    entry = get_object_or_404(Entries, lr_no=lr_no)
    return render(request, 'detail.html', {'entry': entry})


def update_entry(request):
    x = request.POST.get('u_id')
    update = Entries.objects.get(lr_no=x)
    form = forms.AddEntryForm(request.POST)
    return render(request, "update.html", {'update': update, 'form': form})


def save_update(request):
    if request.method == "POST":
        date = request.POST.get('date')
        firm_name = request.POST.get('firm_name')
        lr_no = request.POST.get('lr_no')
        vehicle_no = request.POST.get('vehicle_no').strip()
        location = request.POST.get('location').strip()
        amount = float(request.POST.get('amount'))
        cash = float(request.POST.get('cash'))
        diesel = float(request.POST.get('diesel'))
        rtgs = float(request.POST.get('rtgs'))
        commission = float(request.POST.get('commission'))
        status = request.POST.get('status')
        total_balance = amount - (cash + diesel + rtgs + commission)
        Entries(date=date, firm_name=firm_name, lr_no=lr_no, vehicle_no=vehicle_no, location=location, amount=amount, cash=cash,
                diesel=diesel,rtgs=rtgs,commission=commission, status=status, total_balance=total_balance).save()
        messages.success(request, 'Your entry has been successfully updated')
        return HttpResponseRedirect('/view_entry')


# End Entry CRUD Opreation---------------------------------------------------------

# Delete---------------------------------------------------------
def delete_go(request):
    entry = request.GET.get('delete')
    return render(request, 'delete.html', {'entry': entry})


def delete_entry(request):
    x = request.GET.get('d_id')
    Entries.objects.filter(lr_no=x).delete()
    messages.success(request, "Record Deleted Successfully")
    return view_entry(request)


# End Delete---------------------------------------------------------

# Date Search---------------------------------------------------------
def showresult(request):
    if request.method == 'POST':
        fromdate = request.POST.get('fromdate')
        todate = request.POST.get('todate')
        searchresult = Entries.objects.raw(
            'select date,firm_name,lr_no,vehicle_no,location,amount,cash,diesel,rtgs,commission,status from entries where date between "' + fromdate + '" and "' + todate + '"')
        return render(request, 'date_search.html',
                      {'search_results': searchresult, 'from_date': fromdate, 'to_date': todate})
    else:
        entry = Entries.objects.order_by('-lr_no')
        my_dict = {'search_results': entry}
        return render(request, 'search.html', context=my_dict)


# End Date Search---------------------------------------------------------


# Search---------------------------------------------------------
@login_required
def search(request):
    search = request.GET['search'].strip()
    if search != '':
        search_by_vehicle_no = Entries.objects.filter(vehicle_no__icontains=search)
        search_by_status = Entries.objects.filter(status__icontains=search)
        search_by_lr_no = Entries.objects.filter(lr_no__icontains=search)
        search_results = search_by_vehicle_no.union(search_by_status).union(search_by_lr_no)
        sum_of_vehicle_no = search_by_vehicle_no.aggregate(Sum('total_balance'))
        sum_of_status = search_by_status.aggregate(Sum('total_balance'))
        sum_of_lr_no = search_by_lr_no.aggregate(Sum('total_balance'))
        my_dict = {'search_results': search_results, 'query': search,
                   'sum_of_vehicle_no': sum_of_vehicle_no['total_balance__sum'],
                   'sum_of_status': sum_of_status['total_balance__sum'],
                   'sum_of_lr_no': sum_of_lr_no['total_balance__sum']}
        return render(request, "search.html", context=my_dict)
    else:
        return HttpResponse("<h2>Empty spaces are not allowed.<h2>")


# Search---------------------------------------------------------

# Export Excel---------------------------------------------------------
def export_excel(request):
    search = request.GET.get('excel')
    search_by_vehicle_no = Entries.objects.filter(vehicle_no__icontains=search)
    search_by_status = Entries.objects.filter(status__icontains=search)
    search_by_lr_no = Entries.objects.filter(lr_no__icontains=search)
    search_results = search_by_vehicle_no.union(search_by_status).union(search_by_lr_no).order_by('-lr_no')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'filename="entries.xls"' + \
                                      str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Entries')  # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date','Firm_name' ,'Lr_no', 'Vehicle_no', 'Location', 'Amount', 'Cash', 'Diesel', 'RTGS', 'Commission', 'Total Balance', 'Status']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = search_results.values_list('date','firm_name', 'lr_no', 'vehicle_no', 'location',
                                      'amount', 'cash', 'diesel', 'rtgs', 'commission','total_balance', 'status')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


# Excel Without Search(ALL SHEET)
def export_excel_without_search(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'filename="entries.xls"' + \
                                      str(datetime.datetime.now()) + '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Entries')  # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Date', 'Firm_name', 'Lr_no', 'Vehicle_no', 'Location', 'Amount', 'Cash', 'Diesel', 'RTGS', 'Commission','Total Balance' 'Status']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    rows = Entries.objects.order_by('-lr_no').values_list('date', 'firm_name', 'lr_no', 'vehicle_no', 'location',
                                                          'amount', 'cash', 'diesel', 'rtgs', 'commission','total_balance', 'status')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


# End Export Excel---------------------------------------------------------

# PDF(For Perticular Lr_no)---------------------------------------------------------
def pdf_report_all_create(request):
    entry = Entries.objects.order_by('-lr_no')
    template_path = 'pdf_detail.html'
    context = {'all_entry': entry}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Shri_Ganesh_Transport.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# PDF(For Perticular Lr_no)---------------------------------------------------------
def pdf_report_create(request, pk):
    entry = get_object_or_404(Entries, lr_no=pk)
    template_path = 'pdf_detail.html'
    context = {'entry': entry}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Shri_Ganesh_Transport.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# pdf(For Search Results)
def pdf_report_for_search(request):
    search = request.GET.get('query')
    search_by_vehicle_no = Entries.objects.filter(vehicle_no__icontains=search)
    search_by_status = Entries.objects.filter(status__icontains=search)
    search_by_lr_no = Entries.objects.filter(lr_no__icontains=search)
    search_results = search_by_vehicle_no.union(search_by_status).union(search_by_lr_no).order_by('-lr_no')
    sum_of_vehicle_no = search_by_vehicle_no.aggregate(Sum('total_balance'))
    sum_of_status = search_by_status.aggregate(Sum('total_balance'))
    sum_of_lr_no = search_by_lr_no.aggregate(Sum('total_balance'))
    template_path = 'pdf_detail.html'
    context = {'search_results': search_results,
               'sum_of_vehicle_no': sum_of_vehicle_no['total_balance__sum'],
               'sum_of_status': sum_of_status['total_balance__sum'],
               'sum_of_lr_no': sum_of_lr_no['total_balance__sum']
               }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Shri_Ganesh_Transport.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


# pdf(From Date/To Date)
def from_to_date_pdf(request):
    fromdate = request.POST.get('fromdate')
    todate = request.POST.get('todate')
    print("Excel", fromdate, todate, type(fromdate))
    search_by_from_to_date = Entries.objects.raw(
        'select date,firm_name,lr_no,vehicle_no,location,amount,cash,diesel,rtgs,commission,status from entries where date between "' + fromdate + '" and "' + todate + '"')

    template_path = 'pdf_detail.html'
    context = {'search_results': search_by_from_to_date}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="Shri_Ganesh_Transport.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # if error then show some funny view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response
# End PDF---------------------------------------------------------


# # Export Excel---------------------------------------------------------
# def export_excel_by_from_to_Date(request):
#     if request.method == 'POST':
#         fromdate = request.POST.get('fromdate')
#         todate = request.POST.get('todate')
#         print("Excel",fromdate,todate,type(fromdate))
#         search_by_from_to_date = Entries.objects.raw(
#             'select date,lr_no,vehicle_no,location,amount,cash,diesel,rtgs,commission,status from entries where date between "' + fromdate + '" and "' + todate + '"')
#
#         response = HttpResponse(content_type='application/ms-excel')
#         response['Content-Disposition'] = 'filename="entries.xls"' + \
#                                           str(datetime.datetime.now()) + '.xls'
#
#         wb = xlwt.Workbook(encoding='utf-8')
#         ws = wb.add_sheet('Entries')  # this will make a sheet named Users Data
#
#         # Sheet header, first row
#         row_num = 0
#
#         font_style = xlwt.XFStyle()
#         font_style.font.bold = True
#
#         columns = ['Date', 'Lr_no', 'Vehicle_no', 'Location', 'Amount', 'Cash', 'Diesel', 'RTGS', 'Commission',
#                    'Status']
#
#         for col_num in range(len(columns)):
#             ws.write(row_num, col_num, columns[col_num], font_style)  # at 0 row 0 column
#
#         # Sheet body, remaining rows
#         font_style = xlwt.XFStyle()
#
#         rows = search_by_from_to_date.values_list('date', 'lr_no', 'vehicle_no', 'location',
#                                           'amount', 'cash', 'diesel', 'rtgs', 'commission', 'status')
#         for row in rows:
#             row_num += 1
#             for col_num in range(len(row)):
#                 ws.write(row_num, col_num, str(row[col_num]), font_style)
#
#         wb.save(response)
#
#         return response
#
#     else:
#         entry = Entries.objects.order_by('-lr_no')
#         my_dict = {'search_results': entry}
#         return render(request, 'search.html', context=my_dict)
#
#
# #######################################################
