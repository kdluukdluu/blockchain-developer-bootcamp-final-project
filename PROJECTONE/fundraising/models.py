from django.contrib.auth.models import AbstractUser
from django.db import models
from .utils import *

class User(AbstractUser):
    pass
    
class Project(models.Model):
    image = models.ImageField(upload_to="projects_imgs/", default="")
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    title = models.CharField(max_length=256)
    purpose = models.CharField(max_length=4000, null=True)
    category = models.CharField(max_length=256, null=True)
    goal = models.FloatField(null=True, blank=True)
    deadline = models.DateTimeField(auto_now_add=False, auto_now=False)
    address = models.CharField(max_length=42)
    status = models.CharField(max_length=32, default='Requested')
    userstamp = models.CharField(max_length=64)
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: Image: {self.image} FirstName: {self.firstname} LastName: {self.lastname} Email: {self.email} Title: {self.title} Purpose: {self.purpose} Category: {self.category} Goal: {self.goal} Deadline: {self.deadline} Address: {self.address} createdDate: {self.createdDate} Userstamp: {self.userstamp} Status: {self.status}"

class Category(models.Model):
    category = models.CharField(max_length=64)
    active = models.CharField(max_length=1, default='Y')
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}:Category: {self.category} Active: {self.active} createdDate: {self.createdDate}"

class UserRole(models.Model):
    username = models.CharField(max_length=32)
    role = models.CharField(max_length=32)
    createdDate = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.id}:Role: {self.role} UserName: {self.username} createdDate: {self.createdDate}"

class Request(models.Model):
    description = models.CharField(max_length=1024, null=True)
    value = models.FloatField(null=True, blank=True)
    addressTo = models.CharField(max_length=42)
    numberOfVoters = models.IntegerField(default=0)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="requests")
    requestorEmail = models.CharField(max_length=32, default='None')
    status = models.CharField(max_length=32, default='Requested')
    userstamp = models.CharField(max_length=32, default='None')
    createdDate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: Description: {self.description} Value: {self.value} AddressTo: {self.addressTo} numberOfVoters: {self.numberOfVoters} RequestorEmail: {self.requestorEmail} Status: {self.status} Userstamp: {self.userstamp} createdDate: {self.createdDate}"

    # getting request index for a specific contract
    def getRequestNo(self):
        project = self.project
        requests = Request.objects.filter(project=project.id)

        count = 0

        for request in requests:
            count += 1

            if request == self:
                break

        # index starts from 0 in our contract
        requestNo = count - 1

        return requestNo

     # each request has a related sendPayment function callable only by admin when consensus is reached
    def sendPayment(self):
        requestNo = self.getRequestNo()
        address = self.project.address
        project_contract = web3.eth.contract(abi=abi, address=address)
        transaction = project_contract.functions.makePayment(
            requestNo
        ).buildTransaction(
            {
                "chainId": chain_id,
                "from": my_address,
                "nonce": web3.eth.getTransactionCount(my_address),
            }
        )
        signed_tx = web3.eth.account.sign_transaction(
            transaction, private_key=private_key
        )
        web3.eth.send_raw_transaction(signed_tx.rawTransaction)    