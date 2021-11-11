import brownie

# Test Deployment
def test_deploy(accounts, Fundraising):
    admin = accounts[0]
    # Test Case: The deployment of a new contract goal = 2 ETH deadline = 1 week
    fundraising = Fundraising.deploy(2000000000000000000, 604800, {"from": admin})
    # Assert that this contract is a new one with a balance equal to zero
    expected = 0
    raised_amount = fundraising.raisedAmount()
    assert raised_amount == expected


# Test Donate
def test_donate(accounts, Fundraising):
    admin = accounts[0]
    donor = accounts[1]
    # Creating the contract
    fundraising = Fundraising.deploy(2000000000000000000, 604800, {"from": admin})
    # After the deploment a new user called donor is sending 200 wei to the contract
    fundraising.donate({"from": donor, "value": 200})
    expected = 200
    raised_amount = fundraising.raisedAmount()
    assert expected == raised_amount


# Test Create Request
def test_createRequest(accounts, Fundraising):
    admin = accounts[0]
    recipient = accounts[1]
    fundraising = Fundraising.deploy(2000000000000000000, 604800, {"from": admin})
    # The admin is creating a request with title "Testing Create Request" to send ETH to "recipient" for a value of 200 wei
    fundraising.createRequest("Testing Create Request", recipient, 200, {"from": admin})
    # Verify the parameter status must be Requested for the newly created request
    expected = "Requested"
    status = fundraising.getRequestInfo(0)[3]
    assert expected == status


# Test Vote Request
def test_voteRequest(accounts, Fundraising):
    admin = accounts[0]
    donor = accounts[1]
    recipient = accounts[2]
    fundraising = Fundraising.deploy(2000000000000000000, 604800, {"from": admin})
    # The administrator is creating a request
    fundraising.createRequest("Testing Vote Request", recipient, 200000000000000000, {"from": admin})
    # Donation is required in order to vote a request
    fundraising.donate({"from": donor, "value": 200})
    # The donor is now allowed to vote
    fundraising.voteRequest(0, {"from": donor})
    # Verify the number of voters for the request is now increased by 1
    expected = 1
    number_of_voters = fundraising.getRequestInfo(0)[4]
    assert expected == number_of_voters


# payment test
def test_makePayment(accounts, Fundraising):
    admin = accounts[0]
    donor = accounts[1]
    donation = 200000000000000000
    recipient = accounts[2]
    balance_before_payment = recipient.balance()
    fundraising = Fundraising.deploy(2000000000000000000, 604800, {"from": admin})
    fundraising.createRequest("request", recipient, 200000000000000000, {"from": admin})
    fundraising.donate({"from": donor, "value": donation})
    fundraising.voteRequest(0, {"from": donor})
    # if the quorum is reached the admin can send the payment
    fundraising.makePayment(0, {"from": admin})
    # check the difference of balance after the payment
    balance_after_payment = recipient.balance()
    difference = balance_after_payment - balance_before_payment
    # recipient must have received .2 ETH as settled in the request
    expected = donation
    assert expected == difference
