from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('projectlisting/', views.projectlisting_page, name='projectlisting_page'),
    path('api/other-projects/<int:subdivision_id>/', views.projectlisting, name='projectlisting_api'),
    path('api/subdivisions/by-price-range/<int:city_id>/<str:price_range>/', views.subdivisions_by_price_range, name='subdivisions_by_price_range'),
    path('api/cities/<int:province_id>/', views.get_cities, name='get_cities'),
    path('api/subdivisions/<int:city_id>/', views.get_subdivisions, name='get_subdivisions'),
    path('api/subdivisions/by-province/<int:province_id>/', views.get_subdivisions_by_province, name='get_subdivisions_by_province'),
    path('api/subdivisions/all/', views.get_all_subdivisions, name='get_all_subdivisions'),
    path('api/property/<int:subdivision_id>/', views.get_property_details, name='get_property_details'),
    path('api/subdivisions/search/', views.search_subdivisions, name='search_subdivisions'),

    path('viewproperties/', views.viewproperties, name='viewproperties'),
    path('addproperty/', views.addproperty, name='addproperty'),
    path('addcity/', views.add_city, name='addcity'),
    path('addprovince/', views.add_province, name='addprovince'),
    path('editcity/', views.edit_city, name='editcity'),
    path('editprovince/', views.edit_province, name='editprovince'),
    path('viewproperties/edit/<int:pk>/', views.editproperty, name='editproperty'),
    path('viewproperties/delete/<int:pk>/', views.deleteproperty, name='deleteproperty'),
    path('agentsignin/', views.agentsignin, name='agentsignin'),
    path('agentsignup/', views.agentsignup, name='agentsignup'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('approve/', views.approve_users, name='approve_users'),
    path('signout/', views.signout, name='signout'),
    path('memos/', views.memo_combined_view, name='memo_combined'),
    path('memos/edit/<int:pk>/', views.edit_memo, name='edit_memo'),
    path('memos/delete/<int:pk>/', views.delete_memo, name='delete_memo'),
    path('memos/mark-read/<int:pk>/', views.mark_memo_read, name='mark_memo_read'),
    path('memos/<int:memo_id>/detail/', views.get_memo_detail, name='get_memo_detail'),
    path('get_memo_readers/<int:pk>/', views.get_memo_readers, name='get_memo_readers'),
    path('memos/<int:memo_id>/check-acknowledgment/', views.check_acknowledgment, name='check_acknowledgment'),
    path('search-properties/', views.search_properties, name='search_properties'),


    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)