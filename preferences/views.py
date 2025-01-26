from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken! Please choose another.')
            return redirect('register')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return redirect('register')

        # Create new user if all checks pass
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('preferences')
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url='/login/')
def preferences(request):
    """Main preferences view to display all settings"""
    user = request.user
    preferences_data = {
        'email_notifications': user.email_notifications,
        'push_notifications': user.push_notifications,
        'notification_frequency': user.notification_frequency,
        'theme_color': user.theme_color,
        'font_style': user.font_style,
        'layout_style': user.layout_style or 'list',
        'font_size': user.font_size,
        'profile_visibility': user.profile_visibility,
        'data_sharing': user.data_sharing
    }

    return render(request, 'preferences.html', {'preferences': preferences_data})


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


# @login_required
# def account_settings(request):
#     user = request.user
#
#     if request.method == 'POST':
#         try:
#             user.email_notifications = 'email_notifications' in request.POST
#             user.push_notifications = 'push_notifications' in request.POST
#             user.notification_frequency = request.POST.get('notification_frequency', 'daily')
#             user.theme_color = request.POST.get('theme_color', 'light')
#             user.font_size = request.POST.get('font_size', 'medium')
#             user.profile_visibility = request.POST.get('profile_visibility', 'public')
#             user.data_sharing = 'data_sharing' in request.POST
#             user.save()
#             messages.success(request, "Preferences updated successfully!")
#         except KeyError:
#             messages.error(request, "Some required fields are missing.")
#         except Exception as e:
#             messages.error(request, f"An error occurred: {str(e)}")
#         return redirect('preferences')
#
#     preferences = {
#         'email_notifications': user.email_notifications,
#         'push_notifications': user.push_notifications,
#         'notification_frequency': user.notification_frequency,
#         'profile_visibility': user.profile_visibility,
#         'data_sharing': user.data_sharing,
#     }
#
#     return render(request, 'preferences.html', {'preferences': preferences})

@login_required
def account_settings(request):
    user = request.user

    if request.method == 'POST':
        try:
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password and confirm_password:
                if new_password == confirm_password:
                    user.password = make_password(new_password)
                    messages.success(request, "Password updated successfully!")
                else:
                    messages.error(request, "Passwords do not match!")
                    return redirect('preferences')

            user.email_notifications = 'email_notifications' in request.POST
            user.push_notifications = 'push_notifications' in request.POST
            user.notification_frequency = request.POST.get('notification_frequency', 'daily')
            user.theme_color = request.POST.get('theme_color', 'light')
            user.font_size = request.POST.get('font_size', 'medium')
            user.profile_visibility = request.POST.get('profile_visibility', 'public')
            user.data_sharing = 'data_sharing' in request.POST
            user.save()

            messages.success(request, "Preferences updated successfully!")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
        return redirect('preferences')

    return render(request, 'preferences.html', {'preferences': user})

@login_required
def notification_settings(request):
    user = request.user
    if request.method == 'POST':
        try:
            user.email_notifications = 'email_notifications' in request.POST
            user.push_notifications = 'push_notifications' in request.POST
            notification_frequency = request.POST.get('notification_frequency')
            if notification_frequency in ['daily', 'weekly', 'monthly', 'never']:
                user.notification_frequency = notification_frequency
            else:
                raise ValueError("Invalid notification frequency")

            user.save()
            messages.success(request, "Notification settings updated successfully!")
        except ValueError as e:
            messages.error(request, f"Error: {str(e)}")
        except Exception as e:
            messages.error(request, "An unexpected error occurred while updating notifications.")

        return redirect('preferences')

    return render(request, 'preferences.html', {'preferences': user})


@login_required
def theme_settings(request):
    user = request.user
    if request.method == 'POST':
        try:
            user.theme_color = request.POST.get('theme_color')
            user.font_style = request.POST.get('font_style')
            user.layout_style = request.POST.get('layout_style')
            user.font_size = request.POST.get('font_size')

            user.save()
            messages.success(request, "Theme settings updated successfully!")
        except Exception as e:
            messages.error(request, "An unexpected error occurred while updating theme settings.")

        return redirect('preferences')

    preferences = {
        'theme_color': user.theme_color,
        'font_style': user.font_style,
        'layout_style': user.layout_style,
        'font_size': user.font_size
    }

    return render(request, 'preferences.html', {'preferences': preferences})



@login_required
def privacy_settings(request):
    user = request.user
    if request.method == 'POST':
        try:
            profile_visibility = request.POST.get('profile_visibility')
            if profile_visibility in ['public', 'private']:
                user.profile_visibility = profile_visibility
            else:
                raise ValueError("Invalid profile visibility")

            user.data_sharing = 'data_sharing' in request.POST

            user.save()
            messages.success(request, "Privacy settings updated successfully!")
        except ValueError as e:
            messages.error(request, f"Error: {str(e)}")
        except Exception as e:
            messages.error(request, "An unexpected error occurred while updating privacy settings.")

        return redirect('preferences')

    preferences = {
        'profile_visibility': user.profile_visibility,
        'data_sharing': user.data_sharing
    }

    return render(request, 'preferences.html', {'preferences': preferences})
