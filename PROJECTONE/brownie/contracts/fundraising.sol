//SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.0;

contract Fundraising {
    mapping(address => uint256) public donors;
    address public admin;
    uint256 public numberOfDonors;
    uint256 public minDonation;
    uint256 public deadline; 
    uint256 public goal;
    uint256 public raisedAmount;

    struct Request {
        string description;
        address payable recipient;
        uint256 value;
        string status;
        uint256 numberOfVoters;
        mapping(address => bool) voters;
    }

    mapping(uint256 => Request) public requests;

    uint256 public numberOfRequests;

    constructor(uint256 _goal, uint256 _deadline) {
        goal = _goal;
        deadline = block.timestamp + _deadline;
        minDonation = 200 wei;
        admin = msg.sender;
    }

    event DonateEvent(address _sender, uint256 _value);

    event CreateRequestEvent(
        string _description,
        address _recipient,
        uint256 _value
    );

    event MakePaymentEvent(address _recipient, uint256 _value);

    function donate() public payable {
        require(block.timestamp < deadline, "Deadline has passed!");
        require(msg.value >= minDonation, "Minimum Contribution not met!");

        if (donors[msg.sender] == 0) {
            numberOfDonors++;
        }

        donors[msg.sender] += msg.value;
        raisedAmount += msg.value;

        emit DonateEvent(msg.sender, msg.value);
    }

    receive() external payable {
        donate();
    }

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function getRaisedAmount() public view returns (uint256) {
        return raisedAmount;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only Admin can call this function!");
        _;
    }

    function createRequest(
        string memory _description,
        address payable _recipient,
        uint256 _value
    ) public onlyAdmin {
        Request storage newRequest = requests[numberOfRequests];
        numberOfRequests++;
        newRequest.description = _description;
        newRequest.recipient = _recipient;
        newRequest.value = _value;
        newRequest.status = "Requested";
        newRequest.numberOfVoters = 0;

        emit CreateRequestEvent(_description, _recipient, _value);
    }

    function getRequestInfo(uint256 _requestIndex)
        public
        view
        returns (
            string memory,
            address,
            uint256,
            string memory,
            uint256
        )
    {
        Request storage r = requests[_requestIndex];
        return (
            r.description,
            r.recipient,
            r.value,
            r.status,
            r.numberOfVoters
        );
    }

    function voteRequest(uint256 _requestNo) public {
        require(
            donors[msg.sender] > 0,
            "You must be a donor to vote"
        );
        Request storage thisRequest = requests[_requestNo];

        require(
            thisRequest.voters[msg.sender] == false,
            "You have already voted!"
        );
        thisRequest.voters[msg.sender] = true;
        thisRequest.numberOfVoters++;
    }

    function makePayment(uint256 _requestNo) public onlyAdmin {
        Request storage thisRequest = requests[_requestNo];
        require(
            raisedAmount >= thisRequest.value,
            "You have not raised enough ETH!"
        );
        require(
            keccak256(abi.encodePacked(thisRequest.status)) == keccak256(abi.encodePacked("Requested")),
            "The request has been completed!"
        );
        require(thisRequest.numberOfVoters > numberOfDonors / 2); 

        thisRequest.recipient.transfer(thisRequest.value);
        thisRequest.status = "Completed";

        emit MakePaymentEvent(thisRequest.recipient, thisRequest.value);
    }
}