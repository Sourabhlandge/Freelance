"""shri_ganesh_transport URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from sgt_App import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.index_view),
    path('view_entry/', views.view_entry, name='view_entry'),
    path('<int:lr_no>/', views.entry_detail, name='entry_detail'),
    path('add_entry/', views.add_entry, name='add_entry'),
    path('update_entry/', views.update_entry, name='update_entry'),
    path('save_update/', views.save_update, name='save_update'),
    path('delete_go/', views.delete_go, name='delete_go'),
    path('delete_entry/', views.delete_entry, name='delete_entry'),

    path('search/', views.search, name='search'),  # Search by LR_no, Vehicle_no, Status
    path('showresult/', views.showresult, name='showresult'),  # Search by from-to date

    path('export_excel/', views.export_excel, name='export_excel'),  # Export Excel
    # path('export_excel_by_from_to_Date/',views.export_excel_by_from_to_Date,name='export_excel_by_from_to_Date'),#Export Excel(export_excel_by_from_to_Date)
    path('export_excel_without_search/', views.export_excel_without_search, name='export_excel_without_search'),
    # Export Excel without search

    path('accounts/', include('django.contrib.auth.urls')),
    path('logout/', views.logout_view),

    path('pdf_report_all_create/', views.pdf_report_all_create, name='pdf_report_all_create'),  # pdf for all data
    path('pdf/<int:pk>/', views.pdf_report_create, name='pdf_report'),  # pdf
    path('search_pdf/', views.pdf_report_for_search, name='search_result_pdf'),  # pdf by search
    path('from_to_date_pdf/', views.from_to_date_pdf, name='from_to_date_pdf'),  # pdf by from_to_date

]
