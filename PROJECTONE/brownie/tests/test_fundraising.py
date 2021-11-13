import brownie

# Test Deployment
def test_deploy(accounts, Fundraising):
    # Setup account
    admin = accounts[0]

    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})

    # Assert that this contract is initialized with sysadm=accounts[0]
    expected = admin
    sysadm = fundraising.sysadm()
    assert sysadm == expected

# Test Create Project
def test_createProject(accounts, Fundraising):
    # Setup account
    admin = accounts[0]

    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})

    # Admin creates a new project with goal and deadline
    fundraising.createProject(2000000000000000000, 1640973960000, {"from": admin})

    # Verify projectID is correctly created,
    expected = 1
    projectID = fundraising.numProjects()
    assert expected == projectID   


# Test Donate
def test_donate(accounts, Fundraising):
    # Setup testing accounts
    admin = accounts[0]
    donor = accounts[1]

    # Get balance from the donor account
    balanceBeforeDonation = donor.balance()

    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})
    
    # Create a project
    fundraising.createProject(2000000000000000000, 1640973960000, {"from": admin})
    
    # Get projectID
    projectID = fundraising.numProjects()
    
    # Donor donates 2 ETH to a given projectID
    fundraising.donate(projectID, {"from": donor, "value": 2000000000000000000})
    
    # Get project information
    raisedAmount = fundraising.getProjectInfo(projectID)[5]
    
    # Verify raisedAmount is increased to 2 ETH
    expected = 2000000000000000000
    assert expected == raisedAmount
    
    # Check the difference of balance after the donation
    balanceAfterDonation = donor.balance()
    difference = balanceBeforeDonation - balanceAfterDonation

    # Donor's balance must have 2 ETH less than the original balance.
    expected = 2000000000000000000
    assert expected == difference


# Test Create Request
def test_createRequest(accounts, Fundraising):
    # Setup testing accounts
    admin = accounts[0]
    recipient = accounts[1]

    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})
    
    # Create a project
    fundraising.createProject(2000000000000000000, 1640973960000, {"from": admin})
    
    # Get projectID
    projectID = fundraising.numProjects()
    
    # The admin is creating a request with title "Testing Create Request" to send ETH to "recipient" for a value of 200 wei
    fundraising.createRequest(projectID, "Testing Create Request", recipient, 200, {"from": admin})
    
    # Get requestID
    requestID = fundraising.numberOfRequests()
    
    # Verify the parameter status must be Requested for the newly created request
    expected = "Requested"
    status = fundraising.getRequestInfo(requestID)[4]
    assert expected == status


# Test Vote Request
def test_voteRequest(accounts, Fundraising):
    # Setup testing accounts
    admin = accounts[0]
    donor = accounts[1]
    recipient = accounts[2]
    
    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})
    
    # Create a project
    fundraising.createProject(2000000000000000000, 1640973960000, {"from": admin})
    
    # Get projectID
    projectID = fundraising.numProjects()
    
    # The administrator is creating a request
    fundraising.createRequest(projectID, "Testing Vote Request", recipient, 200000000000000000, {"from": admin})
    
    # Get requestID
    requestID = fundraising.numberOfRequests()
    
    # Donation is required in order to vote a request
    fundraising.donate(projectID, {"from": donor, "value": 200})
    
    # The donor is now allowed to vote
    fundraising.voteRequest(requestID, {"from": donor})
    
    # Verify the number of voters for the request is now increased by 1
    expected = 1
    numberOfVoters = fundraising.getRequestInfo(requestID)[5]
    assert expected == numberOfVoters


# Test Make Payment
def test_makePayment(accounts, Fundraising):
    # Setup testing accounts, donation amount and initial recipient's balance
    admin       = accounts[0]
    donor       = accounts[1]
    recipient   = accounts[2]

    donation = 200000000000000000
    balance_before_payment = recipient.balance()

    # Deploy the contract
    fundraising = Fundraising.deploy({"from": admin})
    
    # Create a project 
    fundraising.createProject(2000000000000000000, 1640973960000, {"from": admin})
    
    # Get projectID
    projectID = fundraising.numProjects()
    
    # Create a request
    fundraising.createRequest(projectID, "request", recipient, 200000000000000000, {"from": admin})
    
    # Get requestID
    requestID = fundraising.numberOfRequests()
    
    # Make a donation
    fundraising.donate(projectID, {"from": donor, "value": donation})
    
    # Make a vote
    fundraising.voteRequest(requestID, {"from": donor})
    
    # Make payment If the consensus is reached
    fundraising.makePayment(requestID, {"from": admin})
    
    # Check the difference of balance after the payment
    balance_after_payment = recipient.balance()
    difference = balance_after_payment - balance_before_payment
    
    # Recipient must have received 2 ETH as settled in the request
    expected = donation
    assert expected == difference
