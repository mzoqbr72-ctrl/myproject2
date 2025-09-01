from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from .models import CustomUser, ActivationToken, PasswordResetToken, Category, Project, ProjectImage, Comment, Donation, Rating, Report
from .email_utils import send_activation_email, send_password_reset_email, send_welcome_email
import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg
from django.core.paginator import Paginator

EGYPTIAN_PHONE_REGEX = r'^(\+20|0)?1[0125][0-9]{8}$'

class RegistrationView(View):
    def get(self, request):
        return render(request, 'pages/register.html')

    def post(self, request):
        data = request.POST
        files = request.FILES
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        mobile_phone = data.get('mobile_phone')
        profile_picture = files.get('profile_picture')

        # Validate required fields
        if not all([first_name, last_name, email, password, confirm_password, mobile_phone]):
            messages.error(request, 'All fields are required.')
            return render(request, 'pages/register.html')

        # Validate password match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'pages/register.html')

        # Validate Egyptian phone number
        if not re.match(EGYPTIAN_PHONE_REGEX, mobile_phone):
            messages.error(request, 'Enter a valid Egyptian mobile phone number.')
            return render(request, 'pages/register.html')

        # Check if email or phone already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'pages/register.html')
        if CustomUser.objects.filter(mobile_phone=mobile_phone).exists():
            messages.error(request, 'Mobile phone already registered.')
            return render(request, 'pages/register.html')

        # Create inactive user
        user = CustomUser.objects.create_user(
            username=email,  # Use email as username
            email=email,
            first_name=first_name,
            last_name=last_name,
            mobile_phone=mobile_phone,
            profile_picture=profile_picture,
            is_active=False
        )
        user.set_password(password)
        user.save()

        # Generate activation token
        token = get_random_string(48)
        ActivationToken.objects.create(user=user, token=token)

        # Send activation email
        activation_link = request.build_absolute_uri(
            reverse('activate', args=[token])
        )
        try:
            if send_activation_email(user, activation_link):
                messages.success(request, 'تم التسجيل بنجاح! يرجى التحقق من بريدك الإلكتروني لتفعيل حسابك.')
            else:
                messages.warning(request, 'تم التسجيل بنجاح! لكن حدث خطأ في إرسال رسالة التفعيل. يرجى التواصل مع الدعم الفني.')
        except Exception as e:
            print(f"Error sending activation email: {e}")
            messages.warning(request, 'تم التسجيل بنجاح! لكن حدث خطأ في إرسال رسالة التفعيل. يرجى التواصل مع الدعم الفني.')
        
        return redirect('register')

class LoginView(View):
    def get(self, request):
        return render(request, 'pages/login.html')

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Account not activated. Please check your email.')
        else:
            messages.error(request, 'Invalid email or password.')
        return render(request, 'pages/login.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        user = request.user
        # Get user's projects
        user_projects = Project.objects.filter(creator=user, is_active=True).order_by('-created_at')
        # Get user's donations
        user_donations = Donation.objects.filter(donor=user).order_by('-created_at')
        
        context = {
            'user_obj': user,
            'user_projects': user_projects,
            'user_donations': user_donations,
        }
        return render(request, 'pages/profile.html', context)

@method_decorator(login_required, name='dispatch')
class ProfileEditView(View):
    def get(self, request):
        return render(request, 'pages/profile_edit.html')

    def post(self, request):
        user = request.user
        data = request.POST
        files = request.FILES
        
        # Update basic info
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.mobile_phone = data.get('mobile_phone', user.mobile_phone)
        
        # Update optional info
        user.birthdate = data.get('birthdate') or None
        user.facebook_profile = data.get('facebook_profile', '')
        user.country = data.get('country', '')
        
        # Handle profile picture
        if 'profile_picture' in files:
            user.profile_picture = files['profile_picture']
        
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

@method_decorator(login_required, name='dispatch')
class ProjectCreateView(View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'pages/project_create.html', {'categories': categories})

    def post(self, request):
        data = request.POST
        files = request.FILES.getlist('images')
        
        # Debug: Print form data
        print("Form data received:", data)
        
        # Validate required fields
        required_fields = ['title', 'details', 'category', 'total_target', 'tags', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
            return self.get(request)
        
        try:
            category = Category.objects.get(id=data.get('category'))
            total_target = float(data.get('total_target'))
            
            # Parse dates and make them timezone-aware
            start_date_str = data.get('start_date')
            end_date_str = data.get('end_date')
            
            print(f"Start date string: {start_date_str}")
            print(f"End date string: {end_date_str}")
            
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d')
            
            # Make dates timezone-aware
            start_date = timezone.make_aware(start_date)
            end_date = timezone.make_aware(end_date)
            
            print(f"Parsed start date: {start_date}")
            print(f"Parsed end date: {end_date}")
            print(f"Current time: {timezone.now()}")
            
            if end_date <= start_date:
                messages.error(request, 'End date must be after start date.')
                return self.get(request)
                
            # Allow projects to start today or in the future
            today = timezone.now().date()
            if start_date.date() < today:
                messages.error(request, 'Start date cannot be in the past.')
                return self.get(request)
                
        except (Category.DoesNotExist, ValueError) as e:
            messages.error(request, f'Invalid data provided: {str(e)}')
            print(f"Error in project creation: {e}")
            return self.get(request)
        
        try:
            # Create project
            project = Project.objects.create(
                creator=request.user,
                title=data.get('title'),
                details=data.get('details'),
                category=category,
                total_target=total_target,
                tags=data.get('tags'),
                start_date=start_date,
                end_date=end_date
            )
            
            # Handle multiple images
            for image_file in files:
                if image_file:
                    ProjectImage.objects.create(project=project, image=image_file)
            
            messages.success(request, 'Project created successfully!')
            return redirect('project_detail', project_id=project.id)
            
        except Exception as e:
            messages.error(request, f'Error creating project: {str(e)}')
            print(f"Error creating project: {e}")
            return self.get(request)

def home(request):
    # Get highest rated projects (top 5 rated)
    highest_rated_projects = Project.objects.filter(
        is_active=True
    ).annotate(
        avg_rating=Avg('ratings__rating')
    ).filter(
        avg_rating__isnull=False
    ).order_by('-avg_rating')[:5]
    
    # Get latest projects
    latest_projects = Project.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Get featured projects (admin selected)
    featured_projects = Project.objects.filter(
        is_active=True, 
        is_featured=True
    ).order_by('-created_at')[:5]
    
    # Get categories
    categories = Category.objects.all()
    
    context = {
        'highest_rated_projects': highest_rated_projects,
        'latest_projects': latest_projects,
        'featured_projects': featured_projects,
        'categories': categories,
    }
    return render(request, "pages/home.html", context)

def game1(request):
    return render(request, "pages/game1.html")

def game2(request):
    return render(request, "pages/game2.html")

def game3(request):
    return render(request, "pages/game3.html")

def project_list(request):
    projects = Project.objects.filter(is_active=True).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(tags__icontains=search_query) |
            Q(details__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category', '')
    if category_id:
        projects = projects.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Category.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id
    }
    return render(request, 'pages/project_list.html', context)

def project_detail(request, project_id):
    try:
        project = Project.objects.get(id=project_id, is_active=True)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found.')
        return redirect('project_list')
    
    # Get average rating
    avg_rating = project.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Get similar projects based on tags
    similar_projects = Project.objects.filter(
        is_active=True,
        tags__icontains=project.tags
    ).exclude(id=project.id)[:4]
    
    # Get comments
    comments = project.comments.filter(parent_comment=None).order_by('-created_at')
    
    context = {
        'project': project,
        'avg_rating': round(avg_rating, 1),
        'similar_projects': similar_projects,
        'comments': comments
    }
    return render(request, 'pages/project_detail.html', context)

@login_required
def donate_to_project(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, is_active=True)
            amount = float(request.POST.get('amount', 0))
            message = request.POST.get('message', '')
            
            if amount <= 0:
                messages.error(request, 'Invalid donation amount.')
                return redirect('project_detail', project_id=project_id)
            
            # Create donation
            donation = Donation.objects.create(
                project=project,
                donor=request.user,
                amount=amount,
                message=message
            )
            
            # Update project current amount
            project.current_amount += amount
            project.save()
            
            messages.success(request, f'Thank you for your donation of {amount} EGP!')
            
        except (Project.DoesNotExist, ValueError):
            messages.error(request, 'Invalid project or amount.')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def rate_project(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, is_active=True)
            rating_value = int(request.POST.get('rating', 0))
            
            if rating_value < 1 or rating_value > 5:
                messages.error(request, 'Invalid rating value.')
                return redirect('project_detail', project_id=project_id)
            
            # Update or create rating
            rating, created = Rating.objects.update_or_create(
                project=project,
                user=request.user,
                defaults={'rating': rating_value}
            )
            
            messages.success(request, 'Rating submitted successfully!')
            
        except (Project.DoesNotExist, ValueError):
            messages.error(request, 'Invalid project or rating.')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def add_comment(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, is_active=True)
            content = request.POST.get('content', '').strip()
            parent_comment_id = request.POST.get('parent_comment')
            
            if not content:
                messages.error(request, 'Comment cannot be empty.')
                return redirect('project_detail', project_id=project_id)
            
            parent_comment = None
            if parent_comment_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_comment_id, project=project)
                except Comment.DoesNotExist:
                    pass
            
            Comment.objects.create(
                project=project,
                user=request.user,
                content=content,
                parent_comment=parent_comment
            )
            
            messages.success(request, 'Comment added successfully!')
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def report_project(request, project_id):
    if request.method == 'POST':
        try:
            project = Project.objects.get(id=project_id, is_active=True)
            reason = request.POST.get('reason', '').strip()
            
            if not reason:
                messages.error(request, 'Please provide a reason for reporting.')
                return redirect('project_detail', project_id=project_id)
            
            Report.objects.create(
                reporter=request.user,
                report_type='project',
                project=project,
                reason=reason
            )
            
            messages.success(request, 'Report submitted successfully. Thank you for helping keep our community safe.')
            
        except Project.DoesNotExist:
            messages.error(request, 'Project not found.')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def cancel_project(request, project_id):
    try:
        project = Project.objects.get(id=project_id, creator=request.user, is_active=True)
        
        if not project.can_be_cancelled():
            messages.error(request, 'Project cannot be cancelled. It has reached more than 25% of its target.')
            return redirect('project_detail', project_id=project_id)
        
        project.is_active = False
        project.save()
        
        messages.success(request, 'Project cancelled successfully.')
        
    except Project.DoesNotExist:
        messages.error(request, 'Project not found or you do not have permission to cancel it.')
    
    return redirect('project_list')

@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password', '')
        
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Please try again.')
            return redirect('profile')
        
        # Delete user account
        user = request.user
        logout(request)
        user.delete()
        
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('home')
    
    return render(request, 'pages/delete_account.html')

def activate_account(request, token):
    try:
        activation = ActivationToken.objects.get(token=token)
        if activation.is_expired():
            activation.delete()
            return render(request, 'pages/activation_error.html', {
                'error_message': 'انتهت صلاحية رابط التفعيل. يرجى التسجيل مرة أخرى.'
            })
        
        user = activation.user
        user.is_active = True
        user.save()
        activation.delete()
        
        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            # Continue even if welcome email fails
        
        return render(request, 'pages/activation_success.html', {
            'user': user
        })
        
    except ActivationToken.DoesNotExist:
        return render(request, 'pages/activation_error.html', {
            'error_message': 'رابط التفعيل غير صحيح أو تم استخدامه من قبل.'
        })
    except Exception as e:
        print(f"Error in activation: {e}")
        return render(request, 'pages/activation_error.html', {
            'error_message': 'حدث خطأ أثناء تفعيل الحساب. يرجى المحاولة مرة أخرى.'
        })

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            # Generate reset token
            token = get_random_string(48)
            PasswordResetToken.objects.create(user=user, token=token)
            
            # Send reset email
            reset_link = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )
            if send_password_reset_email(user, reset_link):
                messages.success(request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.')
            else:
                messages.error(request, 'حدث خطأ في إرسال رسالة إعادة تعيين كلمة المرور. يرجى المحاولة مرة أخرى.')
            return redirect('login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with this email address.')
    
    return render(request, 'pages/forgot_password.html')

def reset_password(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if reset_token.is_expired():
            reset_token.delete()
            messages.error(request, 'Password reset link has expired.')
            return redirect('login')
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                messages.error(request, 'Passwords do not match.')
                return render(request, 'pages/reset_password.html')
            
            # Update password
            user = reset_token.user
            user.set_password(password)
            user.save()
            reset_token.delete()
            
            messages.success(request, 'Password reset successfully. You can now login with your new password.')
            return redirect('login')
        
        return render(request, 'pages/reset_password.html')
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('home')
