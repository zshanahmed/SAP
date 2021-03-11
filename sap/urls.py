from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls import url
from django.contrib.auth.decorators import login_required

app_name = 'sap'
urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='sap/login.html'), name='home'),

    path('logout/', views.logout_request, name='logout'),

    url(r'login_success/$', views.login_success, name='login_success'),

    url(r'^password/$', login_required(views.ChangeAdminPassword.as_view()),
        name='change_password'),
    url(r'^update_profile/$', login_required(views.EditAdminProfile.as_view()),
        name='sap-admin_profile'),

    url(r'^dashboard/$',
        login_required(views.AlliesListView.as_view(), login_url='home'),
        name='sap-dashboard'),

    url('analytics/',
        login_required(views.AnalyticsView.as_view(), login_url='home'),
        name='sap-analytics'),

    url(r'password-forgot/$', views.ForgotPasswordView.as_view(), name='password-forgot'),

    url(r'password-forgot/done/$', views.ForgotPasswordDoneView.as_view(), name='password-forgot-done'),

    url(r'password-forgot/<uidb64>/<token>/$', views.ForgotPasswordConfirmView.as_view(), name='password-forgot-confirm'),

    url(r'password-forgot-mail/', views.ForgotPasswordMail.as_view(), name='password-forgot-mail'),
    #
    # url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',
    #     auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    url(r'password-forgot/complete$', views.ForgotPasswordCompleteView.as_view(), name='password-forgot-complete'),

    url('create_iba_admin/',
        login_required(views.CreateAdminView.as_view(), login_url='home'),
        name='create_iba_admin'),

    url('about/',
        login_required(views.AboutPageView.as_view(), login_url='about'),
        name='sap-about'),

    url('sign-up/', views.SignUpView.as_view(), name='sign-up')
]
