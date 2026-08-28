from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import ClientProfile, LawyerProfile, Case
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def reg_clients(request):
    # Handles Registration for both Clients and Lawyers
    if request.method == "POST":
        user_type = request.POST.get("user_type")

        # Common Data
        email = request.POST.get("email")
        password = request.POST.get("password")
        c_password = request.POST.get("confirm_password")

        # --- 1. VALIDATION (Applies to both) ---
        
        if password != c_password:
            messages.error(request, "Passwords do not match.")
            return redirect("reg_clients")

        if not password or not c_password:
            messages.error(request, "Please fill in all required fields.")
            return redirect("reg_clients")

        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return redirect("reg_clients")

        # --- 2. CLIENT REGISTRATION ---
        
        if user_type == "client":
            F_name = request.POST.get("full_name")
            p_num = request.POST.get("phone")
            address = request.POST.get("address")
            state = request.POST.get("state")

            # Validation
            if not F_name or not email or not p_num:
                messages.error(request, "Please fill in all required fields.")
                return redirect("reg_clients")

            # Create User (Auto-hashes password)
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=F_name,
            )

            # Create Profile
            ClientProfile.objects.create(
                user=user,
                phone=p_num,
                address=address,
                state=state,
            )
            
            messages.success(request, "Client Registration successful! Please log in.")
            return redirect("login")

        # --- 3. LAWYER REGISTRATION ---
        
        elif user_type == "lawyer":
            F_name = request.POST.get("full_name")
            p_num = request.POST.get("phone")
            specialty = request.POST.get("specialty")

            # Validation
            if not F_name or not email or not p_num or not specialty:
                messages.error(request, "Please fill in all required fields.")
                return redirect("reg_clients")

            # Create User
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=F_name,
            )

            # Create Profile
            LawyerProfile.objects.create(
                user=user,
                phone=p_num,
                specialty=specialty,
            )
            
            messages.success(request, "Lawyer Registration successful! Please log in.")
            return redirect("login")

        else:
            messages.error(request, "Invalid selection. Please select Client or Lawyer.")

    return render(request, 'logins-regs/registrations-client.html')


def login_view(request):
    # Handles User Login
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        if not email or not password:
            messages.error(request, 'Email and password must not be empty')
            return redirect('login')

        # Authenticate checks the username field. 
        # Since we saved email as the username during registration, we pass email here.
        user = authenticate(request, username=email, password=password)

        if user is None:
            # Check if user actually exists to give specific feedback
            if not User.objects.filter(email=email).exists():
                 messages.error(request, "No account found with this email.")
            else:
                 messages.error(request, "Invalid password.")
            return redirect("login")

        login(request, user)

        # Redirect based on role
        if hasattr(user, "client_profile"):
            return redirect("client_dashboard")
        elif hasattr(user, "lawyer_profile"):
            return redirect("lawyer_dashboard")
        elif user.is_superuser:
            return redirect("/admin/")
        else:
            messages.error(request, "No profile found for this account.")
            return redirect("login")

    return render(request, 'logins-regs/login.html')


@login_required(login_url='login')
def client_dashboard(request):
    # Displays Client Stats, Form to Submit Case, and Case List
    
    # Security check
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "You don't have access to this page.")
        return redirect("login")
        
    client_profile = request.user.client_profile

    # Handling the "Submit New Case" form from this page
    if request.method == "POST":
        title = request.POST.get("title")
        category = request.POST.get("category")
        description = request.POST.get("description")

        if not title or not category or not description:
            messages.error(request, "Please fill in all fields.")
            return redirect("client_dashboard")

        # Create the Case
        Case.objects.create(
            client=client_profile,
            title=title,
            category=category,
            description=description,
        )
        messages.success(request, "Case submitted successfully!")
        return redirect("client_dashboard")

    # GET Request: Show Dashboard
    # Fetch cases ordered by newest first
    cases = client_profile.cases.all().order_by("-created_at")
    
    context = {
        "cases": cases,
        "pending_count": cases.filter(status="pending").count(),
        "resolved_count": cases.filter(status="resolved").count(),
    }
    return render(request, 'profiles/client_dashboard.html', context)


@login_required(login_url='login')
def lawyer_dashboard(request):
    if not hasattr(request.user, "lawyer_profile"):
        messages.error(request, "Access denied.")
        return redirect("login")

    lawyer_profile = request.user.lawyer_profile

    my_cases = lawyer_profile.cases.all().order_by("-created_at")

    recommended_cases = Case.objects.filter(
        status="pending", lawyer__isnull=True, category=lawyer_profile.specialty
    ).order_by("-created_at")

    other_open_cases = Case.objects.filter(
        status="pending", lawyer__isnull=True
    ).exclude(category=lawyer_profile.specialty).order_by("-created_at")

    context = {
        "lawyer_profile": lawyer_profile,
        "my_cases": my_cases,
        "recommended_cases": recommended_cases,
        "other_open_cases": other_open_cases,
    }
    return render(request, 'profiles/lawyer_dashboard.html', context)


@login_required(login_url='login')
def take_case(request, case_id):
    if request.method == "POST":
        if not hasattr(request.user, "lawyer_profile"):
            messages.error(request, "Access denied.")
            return redirect("login")

        case = Case.objects.get(id=case_id)
        if case.lawyer is not None:
            messages.error(request, "This case has already been taken.")
            return redirect("lawyer_dashboard")

        case.lawyer = request.user.lawyer_profile
        case.status = "in_progress"
        case.save()
        messages.success(request, "Case assigned to you!")

    return redirect("lawyer_dashboard")


def submit_case(request):
    
    # Standalone view to submit a case (if you ever link a button directly here).
    # Currently, submitting happens inside client_dashboard, 
    # but this allows you to submit via url 'submit_case/' as well.
    
    if request.method == "POST":
        # We verify logged in status
        if request.user.is_authenticated and hasattr(request.user, 'client_profile'):
            title = request.POST.get("title")
            category = request.POST.get("category")
            description = request.POST.get("description")
            
            if title and category and description:
                Case.objects.create(
                    client=request.user.client_profile,
                    title=title,
                    category=category,
                    description=description,
                )
                messages.success(request, "Case submitted successfully!")
            else:
                messages.error(request, "Missing fields.")
        else:
            messages.error(request, "Please log in to submit a case.")
    
    return redirect("client_dashboard")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


def dashboard(request):
    # Generic landing page after login (Optional usage)
    if request.user.is_authenticated:
        if hasattr(request.user, "client_profile"):
            return redirect("client_dashboard")
        elif hasattr(request.user, "lawyer_profile"):
            return redirect("lawyer_dashboard")
    
    return redirect("login")

@login_required(login_url='login')
def resolve_case(request, case_id):
    case = Case.objects.get(id=case_id, lawyer=request.user.lawyer_profile)
    case.status = "resolved"
    case.save()
    messages.success(request, "Case marked as resolved.")
    return redirect("lawyer_dashboard")

@login_required(login_url='login')
def case_detail(request, case_id):
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "Access denied.")
        return redirect("login")

    case = Case.objects.get(id=case_id, client=request.user.client_profile)
    return render(request, 'profiles/case_detail.html', {"case": case})


@login_required(login_url='login')
def delete_case(request, case_id):
    if not hasattr(request.user, "client_profile"):
        messages.error(request, "Access denied.")
        return redirect("login")

    case = Case.objects.get(id=case_id, client=request.user.client_profile)

    if case.status != "pending":
        messages.error(request, "You can only delete a case while it's still pending.")
        return redirect("case_detail", case_id=case.id)

    if request.method == "POST":
        case.delete()
        messages.success(request, "Case deleted.")
        return redirect("client_dashboard")

    return redirect("case_detail", case_id=case.id)

@login_required(login_url='login')
def update_profile(request):
    if request.method == "POST":
        if hasattr(request.user, "client_profile"):
            profile = request.user.client_profile
            redirect_to = "client_dashboard"
        elif hasattr(request.user, "lawyer_profile"):
            profile = request.user.lawyer_profile
            redirect_to = "lawyer_dashboard"
        else:
            messages.error(request, "Access denied.")
            return redirect("login")

        full_name = request.POST.get("full_name")
        if full_name:
            request.user.first_name = full_name
            request.user.save()

        if request.FILES.get("avatar"):
            profile.avatar = request.FILES["avatar"]
            profile.save()

        messages.success(request, "Profile updated!")
        return redirect(redirect_to)

    return redirect("login")