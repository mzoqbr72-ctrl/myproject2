from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_activation_email(user, activation_link):
    """
    إرسال رسالة تفعيل الحساب
    """
    subject = 'تفعيل حسابك - CrowdFund Egypt'
    
    # تحضير السياق للقالب
    context = {
        'user': user,
        'activation_link': activation_link,
    }
    
    # تحضير الرسالة HTML
    html_message = render_to_string('emails/activation_email.html', context)
    
    # تحضير الرسالة النصية (بدون HTML)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending activation email: {e}")
        return False


def send_password_reset_email(user, reset_link):
    """
    إرسال رسالة إعادة تعيين كلمة المرور
    """
    subject = 'إعادة تعيين كلمة المرور - CrowdFund Egypt'
    
    # تحضير السياق للقالب
    context = {
        'user': user,
        'reset_link': reset_link,
    }
    
    # تحضير الرسالة HTML
    html_message = render_to_string('emails/password_reset_email.html', context)
    
    # تحضير الرسالة النصية (بدون HTML)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False


def send_welcome_email(user):
    """
    إرسال رسالة ترحيب بعد تفعيل الحساب
    """
    subject = 'مرحباً بك في CrowdFund Egypt! 🎉'
    
    # استخدام رابط نسبي بدلاً من SITE_URL
    projects_url = "/projects/"
    
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #6D9DC5, #4A90E2); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0; font-size: 28px;">🎉 مرحباً بك في CrowdFund Egypt!</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">تم تفعيل حسابك بنجاح</p>
        </div>
        
        <div style="padding: 40px 30px; background: white; border-radius: 0 0 10px 10px;">
            <h2 style="color: #6D9DC5;">مرحباً {user.first_name} {user.last_name}!</h2>
            
            <p style="color: #666; line-height: 1.6;">
                تم تفعيل حسابك بنجاح في منصة CrowdFund Egypt. يمكنك الآن:
            </p>
            
            <ul style="color: #666; line-height: 1.8;">
                <li>🚀 إنشاء مشاريع تمويل جماعي جديدة</li>
                <li>💝 دعم المشاريع المميزة</li>
                <li>💬 التفاعل مع المجتمع</li>
                <li>📊 متابعة تقدم المشاريع</li>
                <li>⭐ تقييم المشاريع والتعليق عليها</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{projects_url}" style="display: inline-block; background: linear-gradient(135deg, #6D9DC5, #4A90E2); color: white; text-decoration: none; padding: 15px 40px; border-radius: 50px; font-weight: 600;">
                    🚀 استكشف المشاريع
                </a>
            </div>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid #6D9DC5; padding: 20px; border-radius: 5px; margin: 30px 0;">
                <h3 style="color: #6D9DC5; margin: 0 0 10px 0;">💡 نصائح للبدء:</h3>
                <p style="margin: 0; color: #666;">
                    • اكمل ملفك الشخصي لإضافة المزيد من المعلومات<br>
                    • استكشف المشاريع الموجودة للتعرف على المنصة<br>
                    • ابدأ بإنشاء مشروعك الأول أو دعم مشروع موجود
                </p>
            </div>
            
            <p style="color: #666; font-size: 14px; text-align: center;">
                إذا كان لديك أي أسئلة، لا تتردد في التواصل معنا.
            </p>
        </div>
        
        <div style="background-color: #f8f9fa; padding: 20px; text-align: center; border-radius: 10px; margin-top: 20px;">
            <p style="margin: 0; color: #666; font-size: 14px;">© 2024 CrowdFund Egypt. جميع الحقوق محفوظة.</p>
        </div>
    </div>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
