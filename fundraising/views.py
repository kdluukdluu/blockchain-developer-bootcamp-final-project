from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage

from .models import User, Project, Category, UserRole, Request

from django.contrib import messages
from decimal import Decimal
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse

from datetime import datetime, timedelta, date
from django.views import generic
from django.utils.safestring import mark_safe

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from datetime import datetime

from .utils import *

def index(request):
    categories = Category.objects.filter(active='Y').order_by('category')
    return render(request, "fundraising/index.html", {"categories":categories})

@login_required
def createproject(request):
    if not request.user.is_authenticated:
        return render(request, "fundraising/register.html", {
            "message": "Creating account will help to easily manage the communication workflow among donors and recipients."
            })

    if request.method == "POST":
        image       = request.FILES['image'] 
        title       = request.POST["title"]
        purpose     = request.POST["purpose"]
        category    = request.POST.getlist("categories")
        goal        = request.POST["goal"]
        deadline    = request.POST["deadline"]
        userstamp   = request.POST["userstamp"]

        #print("abi=", abi)
        #print("bytecode=", bytecode)
        #print("chain_id=", chain_id)
        #print("my_address=", my_address)
        #print("private_key=", private_key)
        #print("deadline=", deadline)

        # Convert deadline from string to datetime format
        dt_deadline = datetime.fromisoformat(deadline)

        # Convert deadline from datetime to integer format
        int_deadline = unix_time_millis(dt_deadline)

        print("int(deadline)=", int_deadline)

        # Call the contract function to create a new project
        projectID = newProject(int(goal), int_deadline)

        print("deployedAddress=", deployedAddress)

        print("projectID=", projectID)

        # Need to save the new contract address in the DB
        address = deployedAddress

        # Get requestor's user record
        user_rec  = User.objects.get(username=userstamp)
        requestorEmail = user_rec.email
        firstname =  user_rec.first_name
        lastname  = user_rec.last_name

        # Get admin's email address
        adminEmail = User.objects.values_list('email', flat=True).get(username='admin')

        # Email the requestor that his/her new fundraising project has been created and saved in blockchain
        recipient_list = []
        subject = 'Thank you for creating a fundraising project.'
        message = 'Your project has been saved in blockchain.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list.append(requestorEmail)
        recipient_list.append(adminEmail)
        #send_mail(subject, message, email_from, recipient_list)

        # Save the project in the DB
        project = Project(status='Requested', projectID=projectID, firstname=firstname, lastname=lastname, email=requestorEmail, title=title, purpose=purpose, category=category, goal=goal, deadline=deadline, address=address, userstamp=userstamp)
        project.image.save(image.name, image)
        project.save()

        categories = Category.objects.filter(active='Y').order_by('category')
        return render(request, "fundraising/createproject.html", {
            "categories":categories,
            "message": "Your project has been created and saved in blockchain."
            })
    else:
        categories = Category.objects.filter(active='Y').order_by('category')
        return render(request, "fundraising/createproject.html", {
            "categories":categories
            })

# Call function createProject in the contract
def newProject(_goal, _deadline):
    project_contract = web3.eth.contract(abi=abi, address=deployedAddress)
        
    transaction = project_contract.functions.createProject(
            _goal, _deadline
        ).buildTransaction(
            {
                "chainId": chain_id,
                "from": my_address,
                "nonce": web3.eth.getTransactionCount(my_address),
            }
        )
    
    signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)  

    # Wait for transaction to be mined
    web3.eth.wait_for_transaction_receipt(tx_hash)

    projectID = getCurrentProjectID()

    print("projectID=", int(projectID))

    return projectID

def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return int(unix_time(dt) * 1000)

# Allow user to make a donation to a given project
@login_required
def donate(request, id):
    project = get_object_or_404(Project, projectID=id)
    context = {"project": project, 
               "contractAddress": deployedAddress}
    return render(request, "fundraising/donate.html", context)

# Allow to make a donation or submit a funding request for a given project
@login_required
def processproject(request, id):
    project = get_object_or_404(Project, projectID=id)
    raisedAmount = getRaisedAmount(id)
    numberOfDonors = getNumberOfDonors(id)
    if request.user.is_superuser:
        role = 'Admin'
    else:
        role = UserRole.objects.values_list('role', flat=True).get(username=request.user)
    context = {
        "project": project,
        "raisedAmount": raisedAmount,
        "numberOfDonors": numberOfDonors,
        "role": role
    }
    return render(request, "fundraising/processproject.html", context)       

# Allow user to see all projects and select one to make a donation or funding request
@login_required
def projects(request, category='None'):
    if category == 'None':
        projects = Project.objects.all()
    else:
        projects = Project.objects.filter(category__contains=category)

    context = {
        "projects": projects,
    }
    return render(request, "fundraising/projects.html", context) 

# List all requests for a given project
@login_required
def requests(request, id):
    project = get_object_or_404(Project, projectID=id)
    open_requests = Request.objects.filter(project=project, status='Requested')
    complete_requests = Request.objects.filter(project=project, status='Completed')

    context = {
        "project": project,
        "open_requests": open_requests,
        "complete_requests": complete_requests,
    }

    return render(request, "fundraising/requests.html", context)  

# Create a new request - only administrators can propose a request
@login_required
def createrequest(request, id=0):
    if request.method == "POST":
        description = request.POST["description"]
        value       = request.POST["value"]
        addressTo   = request.POST["addressTo"]
        userstamp   = request.POST["userstamp"]
        projectID   = request.POST["projectID"]
        project = get_object_or_404(Project, projectID=projectID)

         # Get requestor's user record
        user_rec  = User.objects.get(username=userstamp)
        requestorEmail = user_rec.email

        # Call the contract for this specific project and create a request
        requestID = newRequest(int(projectID), description, addressTo, int(value))

        # Save the request in the DB
        request = Request(status='Requested', requestID=requestID, description=description, value=value, addressTo=addressTo, project=project, requestorEmail=requestorEmail, userstamp=userstamp)
        request.save()

        return redirect(f"/projects/{projectID}/requests")

    project = get_object_or_404(Project, projectID=id)
    context = {
        "project": project,
    }

    return render(request, "fundraising/createrequest.html", context)

# Call function createRequest in the contract
def newRequest(_projectID, _description, _recipient, _value):
    project_contract = web3.eth.contract(abi=abi, address=deployedAddress)
        
    transaction = project_contract.functions.createRequest(
        _projectID, _description, _recipient, _value
        ).buildTransaction(
            {
                "chainId": chain_id,
                "from": my_address,
                "nonce": web3.eth.getTransactionCount(my_address),
            }
        )

    signed_tx = web3.eth.account.sign_transaction(transaction, private_key=private_key)

    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)  

    # Wait for transaction to be mined
    web3.eth.wait_for_transaction_receipt(tx_hash)

    requestID = getCurrentRequestID()

    print("requestID=", int(requestID))

    return requestID  
      
# Process request page - Allow user to Vote or Make Payment for a given request.
@login_required
def processrequest(request, id):

    req = get_object_or_404(Request, requestID=id)
    projectID = req.project.projectID
    numberOfVoters = getNumberOfVoters(id)
    numberOfDonors = getNumberOfDonors(projectID)

    # Calculate consensus for this request
    if numberOfDonors == 0:
        consensus = 0
    else:
        consensus = float((float(numberOfVoters) / float(numberOfDonors))) * 100

    context = {
        "request": req,
        "numberOfVoters": numberOfVoters,
        "requestNo": id,
        "consensus": consensus,
    }

    return render(request, "fundraising/processrequest.html", context)      

# Page for completing a request - action from the back end since only superuser can call this function
@login_required
def makepayment(request, id):
    req = get_object_or_404(Request, requestID=id)
    req.sendPayment()
    req.status = 'Completed'
    req.save()

    return redirect("/")

# Vote page - actions are built in the front end with web3.js
@login_required
def vote(request, id):
    req = get_object_or_404(Request, requestID=id)

    context = {
        "request": req,
        "requestNo": id,
    }

    return render(request, "fundraising/vote.html", context)

def category(request):
    categories = Category.objects.filter(active='Y').order_by('category')

    return render(request, "fundraising/category.html", {
        "categories": categories
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "fundraising/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "fundraising/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        role = request.POST["role"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "fundraising/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return render(request, "fundraising/register.html", {
                "message": "Username already taken."
            })

        # Create new user role
        userrole = UserRole(username=username, role=role)
        userrole.save()
        
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "fundraising/register.html")

def myprofile(request):
    # Get logged in user's role and user record
    if request.user.is_authenticated: 
        if request.user.is_superuser:
            role = 'Admin'
        else:
            role = UserRole.objects.values_list('role', flat=True).get(username=request.user)
        userinfo = User.objects.filter(username=request.user).values_list('first_name','last_name','date_joined','email','username')
        first_name = userinfo[0][0]
        last_name = userinfo[0][1]
        date_joined = userinfo[0][2]
        email = userinfo[0][3]
        username = userinfo[0][4]
        
        return render(request, "fundraising/myprofile.html", {
            "first_name": first_name,
            "last_name": last_name,
            "date_joined": date_joined,
            "email": email,
            "username": username,
            "role": role
        })
    else:
        return render(request, "fundraising/myprofile.html")

def change_password(request):
    ack_message = ''
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            ack_message = 'Your password was successfully updated!'
            # return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'fundraising/change_password.html', {
        'form': form,
        'message': ack_message
    })
