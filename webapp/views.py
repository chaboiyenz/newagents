from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.views import *
from django.http import JsonResponse
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.utils import timezone
from django.db.models import Q
from datetime import datetime


def admin_check(user):
    return user.is_superuser  # Only allow admin users

def index(request):
    return redirect('projectlisting_page')  # Redirect to projectlisting page


@login_required
def projectlisting_page(request):
    provinces = Province.objects.prefetch_related('cities__subdivisions__projects').all()

    # Determine if filters are selected (optional: pull from GET parameters if used)
    provinces_selected = request.GET.get('province') is not None
    city_selected = request.GET.get('city') is not None
    price_range_selected = request.GET.get('price_range') is not None

    # Fallback data: top priority subdivisions, if no filters selected
    top_priority_subdivisions = []
    if not provinces_selected and not city_selected and not price_range_selected:
        top_priority_subdivisions = Subdivision.objects.filter(priority='high')[:6]

    context = {
        'provinces': provinces,
        'top_priority_subdivisions': top_priority_subdivisions,
        'provinces_selected': provinces_selected,
        'city_selected': city_selected,
        'price_range_selected': price_range_selected,
    }

    return render(request, 'projectlisting.html', context)

def projectlisting(request, subdivision_id):
    try:
        subdivision = Subdivision.objects.select_related('city').get(pk=subdivision_id)
        city = subdivision.city
        other_subdivisions = city.subdivisions.exclude(pk=subdivision_id)
        other_projects = Project.objects.filter(subdivision__in=other_subdivisions).select_related('subdivision')

        project_data = [{
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'price_range': project.price_range_display,
            'commission': subdivision.commission,  # Use the commission from the subdivision model
            'image1': project.image.url if project.image else None,
            'image2': project.image2.url if hasattr(project, 'image2') and project.image2 else None,
            'image3': project.image3.url if hasattr(project, 'image3') and project.image3 else None,
            'image4': project.image4.url if hasattr(project, 'image4') and project.image4 else None,
            'image': project.image.url if project.image else None,
        } for project in other_projects]

        return JsonResponse({'projects': project_data})
    except Subdivision.DoesNotExist:
        return JsonResponse({'projects': []})



def subdivisions_by_price_range(request, city_id, price_range):
    try:
        min_price_str, max_price_str = price_range.split('-')
        min_price = int(min_price_str)
        max_price = int(max_price_str) if max_price_str else None

        # Initial query for subdivisions in the city
        subdivisions = Subdivision.objects.filter(city_id=city_id).select_related('city__province')

        # Apply price range filtering
        if max_price:
            subdivisions = subdivisions.filter(price_max__gte=min_price, price_min__lte=max_price)
        else:
            subdivisions = subdivisions.filter(price_max__gte=min_price)

        # Sort by priority (high -> medium -> low)
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        subdivisions = sorted(subdivisions, key=lambda x: priority_order.get(x.priority or 'low'))

        data = []
        for sub in subdivisions:
            data.append({
                "id": sub.id,
                "name": sub.name,
                "description": sub.description or '',
                "price_range_display": sub.price_range_display,
                "priority": sub.priority or 'low',
                "image1": sub.image1.url if sub.image1 else '',
                "image2": sub.image2.url if sub.image2 else '',
                "image3": sub.image3.url if sub.image3 else '',
                "image4": sub.image4.url if sub.image4 else '',
                "messenger_link": sub.messenger_link or '',
                "google_drive_link": sub.google_drive_link or '',
                "construction_status": sub.construction_status or '',
                "developer": sub.developer or '',
                "commission": float(sub.commission),
                "city": sub.city.name,
                "province": sub.city.province.name,
                "location": sub.location or '',
                "house_model": sub.house_model or ''
            })

        return JsonResponse({"subdivisions": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def search_subdivisions(request):
    query = request.GET.get('q', '').strip()
    if query:
        subdivisions = Subdivision.objects.filter(
            Q(name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(city__province__name__icontains=query)
        ).select_related('city__province')

        data = []
        for sub in subdivisions:
            data.append({
                "id": sub.id,
                "name": sub.name,
                "description": sub.description or '',
                "price_range_display": sub.price_range_display,
                "priority": sub.priority or 'low',
                "image1": sub.image1.url if sub.image1 else '',
                "image2": sub.image2.url if sub.image2 else '',
                "image3": sub.image3.url if sub.image3 else '',
                "image4": sub.image4.url if sub.image4 else '',
                "messenger_link": sub.messenger_link or '',
                "google_drive_link": sub.google_drive_link or '',
                "construction_status": sub.construction_status or 'Not specified',
                "developer": sub.developer or 'Not specified',
                "commission": float(sub.commission),
                "city": sub.city.name,
                "province": sub.city.province.name,
                "price_min": sub.price_min,
                "price_max": sub.price_max,
                "location": sub.location or '',
                "house_model": sub.house_model or ''
            })

        return JsonResponse({"subdivisions": data})
    return JsonResponse({"subdivisions": []})


def get_cities(request, province_id):
    try:
        province = Province.objects.get(id=province_id)
        cities = province.cities.all()  
        
        city_data = [{"id": city.id, "name": city.name} for city in cities]
        return JsonResponse({"cities": city_data})
    except Province.DoesNotExist:
        return JsonResponse({"cities": []})


def get_subdivisions(request, city_id):
    """
    Get all subdivisions for a city regardless of price range,
    ordered by priority (high, medium, low)
    """
    try:
        # Create a custom ordering for priority
        subdivisions = Subdivision.objects.filter(city_id=city_id).select_related('city__province')
        
        # Sort subdivisions by priority (high -> medium -> low)
        priority_order = {'low': 1, 'medium': 2, 'high': 3}
        subdivisions = sorted(subdivisions, key=lambda x: priority_order.get(x.priority or 'low'))
        
        data = []
        for sub in subdivisions:
            data.append({
                "id": sub.id,
                "name": sub.name,
                "description": sub.description or '',
                "price_range_display": sub.price_range_display,
                "priority": sub.priority or 'low',
                "image1": sub.image1.url if sub.image1 else '',
                "image2": sub.image2.url if sub.image2 else '',
                "image3": sub.image3.url if sub.image3 else '',
                "image4": sub.image4.url if sub.image4 else '',
                "messenger_link": sub.messenger_link or '',
                "google_drive_link": sub.google_drive_link or '',
                "construction_status": sub.construction_status or '',
                "developer": sub.developer or '',
                "commission": float(sub.commission),
                "city": sub.city.name,
                "province": sub.city.province.name,
                "location": sub.location or '',
                "house_model": sub.house_model or ''
            })
        
        return JsonResponse({"subdivisions": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_property_details(request, subdivision_id):
    try:
        subdivision = Subdivision.objects.select_related('city__province').get(id=subdivision_id)

        subdivision_data = {
            "id": subdivision.id,
            "name": subdivision.name,
            "description": subdivision.description,
            "price_range_display": subdivision.price_range_display,
            "commission": float(subdivision.commission),
            "priority": subdivision.priority,
            "messenger_link": subdivision.messenger_link or '',
            "image1": subdivision.image1.url if subdivision.image1 else '',
            "city": subdivision.city.name,
            "province": subdivision.city.province.name,
        }

        return JsonResponse({"subdivision": subdivision_data})
    except Subdivision.DoesNotExist:
        return JsonResponse({"subdivision": None})



@login_required
def viewproperties(request):
    query = request.GET.get('q', '')
    price = request.GET.get('price', '')
    
    subdivisions = Subdivision.objects.all()
    
    if query:
        subdivisions = subdivisions.filter(name__icontains=query) | \
                        subdivisions.filter(city__name__icontains=query) | \
                        subdivisions.filter(city__province__name__icontains=query)
    
    if price:
        if price == 'range1':  # Below 500,000
            subdivisions = subdivisions.filter(price_max__lte=500000)
        elif price == 'range2':  # 500,000 - 1,000,000
            subdivisions = subdivisions.filter(price_min__gte=500000, price_max__lte=1000000)
        elif price == 'range3':  # 1,000,000 - 2,000,000
            subdivisions = subdivisions.filter(price_min__gte=1000000, price_max__lte=2000000)
        elif price == 'range4':  # 2,000,000 - 5,000,000
            subdivisions = subdivisions.filter(price_min__gte=2000000, price_max__lte=5000000)
        elif price == 'range5':  # 5,000,000 - 10,000,000
            subdivisions = subdivisions.filter(price_min__gte=5000000, price_max__lte=10000000)
        elif price == 'range6':  # Above 10,000,000
            subdivisions = subdivisions.filter(price_min__gte=10000000)
    
    return render(request, 'viewproperties.html', {'subdivisions': subdivisions, 'query': query, 'price': price})

@login_required
def addproperty(request):
    if request.method == 'POST':
        form = SubdivisionForm(request.POST, request.FILES)
        
        # Debug output
        print("Form submitted with data:", request.POST)
        print("Files submitted:", request.FILES)
        
        if form.is_valid():
            subdivision = form.save()
            messages.success(request, f'Subdivision "{subdivision.name}" added successfully!')
            return redirect('addproperty')  # Redirect to the same page after submission
        else:
            # Print detailed errors for debugging
            print("Form errors:", form.errors)
            if form.non_field_errors():
                print("Non-field errors:", form.non_field_errors())
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SubdivisionForm()

    city_form = CityForm()
    province_form = ProvinceForm()

    return render(request, 'addproperty.html', {
        'form': form,
        'city_form': city_form,
        'province_form': province_form,
    })




@login_required
def add_city(request):
    if request.method == 'POST':
        city_form = CityForm(request.POST)
        if city_form.is_valid():
            city_form.save()  # Save the city
            return redirect('addproperty')  # Redirect to the same page after saving
    else:
        city_form = CityForm()

    form = SubdivisionForm()
    province_form = ProvinceForm()

    return render(request, 'addproperty.html', {
        'form': form,
        'city_form': city_form,
        'province_form': province_form,
    })


@login_required
def add_province(request):
    if request.method == 'POST':
        province_form = ProvinceForm(request.POST)
        if province_form.is_valid():
            province_form.save()  # Save the province
            return redirect('addproperty')  # Redirect to the same page after saving
    else:
        province_form = ProvinceForm()

    form = SubdivisionForm()
    city_form = CityForm()

    return render(request, 'addproperty.html', {
        'form': form,
        'province_form': province_form,
        'city_form': city_form,
    })





@login_required
def editproperty(request, pk):
    subdivision = get_object_or_404(Subdivision, pk=pk)
    if request.method == 'POST':
        form = SubdivisionForm(request.POST, request.FILES, instance=subdivision)
        if form.is_valid():
            form.save()
            return redirect('viewproperties')
    else:
        form = SubdivisionForm(instance=subdivision)

    return render(request, 'editproperty.html', {'form': form})



@login_required
def deleteproperty(request, pk):
    subdivision = get_object_or_404(Subdivision, pk=pk)
    subdivision.delete()
    return redirect('viewproperties')

def agentsignin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'profile') and user.profile.is_approved:
                login(request, user)
                return redirect('/projectlisting/')
            else:
                messages.error(request, 'Your account is not approved yet.')
                return redirect('agentsignin')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'agentsignin.html')

def agentsignup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if password != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('agentsignup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('agentsignup')

        # Create the user
        user = User.objects.create_user(username=username, password=password, email=email)
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # Notify admin via email
        send_mail(
            subject='Bagong Agent Signup sa Inner SPARC Realty',
            message=(
                f'Hi Admin,\n\n'
                f'May bagong agent na nag-sign up sa system ng Inner SPARC Realty Corporation.\n\n'
                f'Narito ang details niya:\n'
                f'👤 Username: {username}\n'
                f'📛 Pangalan: {first_name} {last_name}\n'
                f'📧 Email: {email}\n\n'
                f'Paki-review na lang po ang account niya kapag may time. Let us know if any action is needed.\n\n'
                f'Auto-generated message lang ito from the system — no need to reply.\n\n'
                f'Salamat!\n'
                f'Inner SPARC Realty Corporation'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin[1] for admin in settings.ADMINS],
            fail_silently=False,
        )

        # Add success message
        messages.success(request, 'Account created successfully! Your account is pending for approval.')

        return redirect('agentsignin')

    return render(request, 'agentsignup.html')



@user_passes_test(admin_check)
@login_required
def approve_users(request):
    if request.method == 'POST':
        if 'approve_all' in request.POST:
            # Handle approve all
            unapproved_profiles = Profile.objects.filter(is_approved=False)
            approved_count = 0
            
            for profile in unapproved_profiles:
                profile.is_approved = True
                profile.save()
                
                # Send approval email for each user
                subject = 'Your account has been approved'
                message = f"""Hi {profile.user.first_name},

Good day! We're happy to inform you that your account with *Inner SPARC Realty Corporation* has been **successfully approved**.

You may now log in and start exploring the platform — including available projects, properties, and all other features designed to support your real estate journey.

Kung may kailangan po kayo or may questions, feel free to reach out to us anytime.

Thank you for being part of Inner SPARC Realty!

Best regards,  
Inner SPARC Realty Corporation Support Team
"""
                recipient = profile.user.email
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])
                approved_count += 1
            
            if approved_count > 0:
                messages.success(request, f'Successfully approved {approved_count} users!')
            else:
                messages.info(request, 'No users to approve.')
            
            return redirect('approve_users')
        elif 'update_role' in request.POST:
            # Handle role update
            user_id = request.POST.get('user_id')
            role = request.POST.get('role')
            try:
                user = User.objects.get(id=user_id)
                # Update user roles
                if role == 'superuser':
                    user.is_superuser = True
                    user.is_staff = True
                elif role == 'staff':
                    user.is_superuser = False
                    user.is_staff = True
                else:  # none
                    user.is_superuser = False
                    user.is_staff = False
                user.save()
                messages.success(request, f'Successfully updated role for {user.username}')
            except User.DoesNotExist:
                messages.error(request, 'User not found')
            return redirect('approve_users')
        else:
            # Handle single user approval
            user_id = request.POST.get('user_id')
            try:
                profile = Profile.objects.get(user__id=user_id)
                profile.is_approved = True
                profile.save()  

                # Send approval email
                subject = 'Your account has been approved'
                message = f"""Hi {profile.user.first_name},

Good day! We're happy to inform you that your account with *Inner SPARC Realty Corporation* has been **successfully approved**.

You may now log in and start exploring the platform — including available projects, properties, and all other features designed to support your real estate journey.

Kung may kailangan po kayo or may questions, feel free to reach out to us anytime.

Thank you for being part of Inner SPARC Realty!

Best regards,  
Inner SPARC Realty Corporation Support Team
"""

                recipient = profile.user.email
                send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient])

                messages.success(request, 'User approved successfully and email sent!')
            except Profile.DoesNotExist:
                messages.error(request, 'User not found')
            return redirect('approve_users')

    # Get all users, not just unapproved ones
    users = Profile.objects.all()
    return render(request, 'approve.html', {'users': users})

def signout(request):
    logout(request)
    return redirect('agentsignin')

def get_memo_readers(request, pk):
    """
    AJAX view to get all readers for a specific memo
    """
    # No authentication check to allow seeing readers even when not logged in
    try:
        memo = Memo.objects.get(pk=pk)
        readers = MemoReadStatus.objects.filter(memo=memo).select_related('employee')
        reader_usernames = [reader.employee.username for reader in readers]
        
        return JsonResponse({
            'memo_title': memo.title,
            'readers': reader_usernames,
            'count': len(reader_usernames)
        })
    except Memo.DoesNotExist:
        return JsonResponse({'error': 'Memo not found'}, status=404)
    
@login_required
def get_memo_detail(request, memo_id):
    try:
        memo = get_object_or_404(Memo, id=memo_id)
        
        # Get read status for the current user
        read_status = MemoReadStatus.objects.filter(
            memo=memo,
            employee=request.user
        ).first()
        
        response_data = {
            'id': memo.id,
            'title': memo.title,
            'description': memo.description,
            'when': memo.when.isoformat(),
            'where': memo.where,
            'file_url': memo.file.url if memo.file else None,
            'acknowledged': bool(read_status and read_status.read),
            'acknowledged_date': read_status.read_at.strftime('%Y-%m-%d %H:%M') if read_status and read_status.read_at else None,
        }
        
        print(f"Sending memo details: {response_data}")  # Debug log
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error in get_memo_detail: {str(e)}")  # Debug log
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def check_acknowledgment(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id)
    read_status = MemoReadStatus.objects.filter(
        memo=memo,
        employee=request.user
    ).first()
    
    return JsonResponse({
        'acknowledged': bool(read_status and read_status.read),
        'acknowledged_date': read_status.read_at.strftime('%Y-%m-%d %H:%M') if read_status and read_status.read_at else None,
    })

@login_required
def mark_memo_read(request, pk):
    memo = get_object_or_404(Memo, pk=pk)
    
    # Get or create the read status
    read_status, created = MemoReadStatus.objects.get_or_create(
        employee=request.user,
        memo=memo,
        defaults={'read': True, 'read_at': timezone.now()}
    )
    
    # If not created, update the existing one
    if not created:
        read_status.read = True
        read_status.read_at = timezone.now()
        read_status.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'acknowledged_date': read_status.read_at.strftime('%Y-%m-%d %H:%M'),
        })

    return redirect('memo_combined')


@login_required
def memo_combined_view(request):
    try:
        form = MemoForm(request.POST or None, request.FILES or None)

        if request.method == 'POST' and form.is_valid():
            memo = form.save()
            
            # Send email notifications to all employees
            all_employees = User.objects.filter(is_active=True).exclude(is_superuser=True)
            
            for employee in all_employees:
                subject = 'New Memo Notification - Inner SPARC Realty'
                message = f"""
Hi {employee.first_name},

A new memo has been posted in the Inner SPARC Realty system.

Title: {memo.title}
When: {memo.when.strftime('%B %d, %Y %I:%M %p')}
Where: {memo.where if memo.where else 'Not specified'}

Please log in to your account to view the complete memo and acknowledge receipt.

Best regards,
Inner SPARC Realty Management
"""
                try:
                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[employee.email],
                        fail_silently=True
                    )
                except Exception as e:
                    print(f"Failed to send email to {employee.email}: {str(e)}")

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('memo_combined')

        # Filtering
        query = request.GET.get('q')
        date = request.GET.get('date')
        print(f"Received request - Query: {query}, Date: {date}")  # Debug log
        
        # Start with all memos and order by most recent first
        memos = Memo.objects.all().order_by('-when')
        print(f"Initial memo count: {memos.count()}")  # Debug log

        # Apply filters if they exist
        if query:
            memos = memos.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if date:
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                memos = memos.filter(when__date=date_obj)
                print(f"Filtered by date {date_obj}, memo count: {memos.count()}")  # Debug log
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")  # Debug log
                pass

        # Pagination
        try:
            paginator = Paginator(memos, 10)  # Show 10 memos per page
            page_number = request.GET.get('page', 1)  # Default to first page if not specified
            page_obj = paginator.get_page(page_number)
            print(f"Page {page_number} of {paginator.num_pages}, items: {len(page_obj)}")  # Debug log
        except Exception as e:
            print(f"Pagination error: {e}")  # Log any pagination errors
            page_obj = []

        # Read status for current user
        read_memo_ids = set()
        if request.user.is_authenticated:
            read_memo_ids = set(MemoReadStatus.objects.filter(
                employee=request.user, 
                read=True
            ).values_list('memo_id', flat=True))

        # Handle AJAX requests
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                memo_list = []
                for memo in page_obj:
                    memo_data = {
                        'id': memo.id,
                        'title': memo.title,
                        'description': memo.description,
                        'when': memo.when.isoformat(),
                        'where': memo.where,
                        'file_url': memo.file.url if memo.file else None,
                        'is_read': memo.id in read_memo_ids
                    }
                    memo_list.append(memo_data)
                
                response_data = {
                    'memos': memo_list,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages
                }
                print(f"Sending JSON response with {len(memo_list)} memos")  # Debug log
                return JsonResponse(response_data)
            except Exception as e:
                print(f"Error preparing JSON response: {str(e)}")  # Debug log
                return JsonResponse({'error': str(e)}, status=500)

        context = {
            'form': form,
            'page_obj': page_obj,
            'query': query,
            'date': date,
            'read_memo_ids': read_memo_ids,
        }

        return render(request, 'memo.html', context)
    except Exception as e:
        print(f"Unexpected error in memo_combined_view: {str(e)}")  # Debug log
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': str(e)}, status=500)
        raise  # Re-raise the exception for non-AJAX requests


@login_required
def edit_memo(request, pk):
    memo = get_object_or_404(Memo, pk=pk)
    if request.method == 'POST':
        form = MemoForm(request.POST, request.FILES, instance=memo)
        if form.is_valid():
            form.save()
            return redirect('memo_combined')
    else:
        form = MemoForm(instance=memo)
    return render(request, 'edit_memo.html', {'form': form, 'memo': memo})


@login_required
def delete_memo(request, pk):
    memo = get_object_or_404(Memo, pk=pk)
    memo.delete()
    return redirect('memo_combined')

@login_required
def search_properties(request):
    query = request.GET.get('q', '')
    price = request.GET.get('price', '')
    
    subdivisions = Subdivision.objects.all()
    
    if query:
        subdivisions = subdivisions.filter(
            Q(name__icontains=query) |
            Q(city__name__icontains=query) |
            Q(city__province__name__icontains=query)
        )
    
    if price:
        if price == 'range1':  # Below 500,000
            subdivisions = subdivisions.filter(price_max__lte=500000)
        elif price == 'range2':  # 500,000 - 1,000,000
            subdivisions = subdivisions.filter(price_min__gte=500000, price_max__lte=1000000)
        elif price == 'range3':  # 1,000,000 - 2,000,000
            subdivisions = subdivisions.filter(price_min__gte=1000000, price_max__lte=2000000)
        elif price == 'range4':  # 2,000,000 - 5,000,000
            subdivisions = subdivisions.filter(price_min__gte=2000000, price_max__lte=5000000)
        elif price == 'range5':  # 5,000,000 - 10,000,000
            subdivisions = subdivisions.filter(price_min__gte=5000000, price_max__lte=10000000)
        elif price == 'range6':  # Above 10,000,000
            subdivisions = subdivisions.filter(price_min__gte=10000000)

    data = []
    for s in subdivisions:
        price_class = ''
        if s.price_min < 500000:
            price_class = 'bg-green-100 text-green-800'
        elif s.price_min < 1000000:
            price_class = 'bg-blue-100 text-blue-800'
        elif s.price_min < 2000000:
            price_class = 'bg-yellow-100 text-yellow-800'
        elif s.price_min < 5000000:
            price_class = 'bg-purple-100 text-purple-800'
        elif s.price_min < 10000000:
            price_class = 'bg-pink-100 text-pink-800'
        else:
            price_class = 'bg-red-100 text-red-800'

        data.append({
            'id': s.id,
            'name': s.name,
            'province': s.city.province.name,
            'city': s.city.name,
            'price_min': s.price_min,
            'price_max': s.price_max,
            'price_class': price_class
        })

    return JsonResponse({'subdivisions': data})