//SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.0;

contract Fundraising {
    
    address public sysadm;
    
    struct Project {
        address admin;
        uint256 numberOfDonors;
        uint256 minDonation;
        uint256 deadline; 
        uint256 goal;
        uint256 raisedAmount;
        mapping(address => uint256) donors;
    }
    
    uint256 public numProjects;
    mapping (uint256 => Project) projects;

    struct Request {
        uint256 projectID;
        string  description;
        address payable recipient;
        uint256 value;
        string  status;
        uint256 numberOfVoters;
        mapping(address => bool) voters;
    }

    mapping(uint256 => Request) public requests;

    uint256 public numberOfRequests;
    
    constructor() {
        sysadm = msg.sender;
    }
    
    event CreateProjectEvent(uint256 _projectID, uint256 _goal, uint256 _deadline);

    event DonateEvent(uint256 _projectID, address _sender, uint256 _value);

    event CreateRequestEvent(uint256 _projectID, string _description, address _recipient, uint256 _value);

    event MakePaymentEvent(address _recipient, uint256 _value);
    
    function createProject(uint256 _goal, uint256 _deadline) public returns (uint256 projectID) {
        numProjects = numProjects + 1; 
        projectID = numProjects; // projectID is return variable
        Project storage p = projects[projectID];
        p.goal = _goal;
        p.deadline = block.timestamp + _deadline;
        p.minDonation = 200 wei;
        p.admin = msg.sender;
        
        emit CreateProjectEvent(projectID, _goal, _deadline);
    }

    function getProjectInfo(uint256 _projectID)
        public
        view
        returns (
            address,
            uint256,
            uint256,
            uint256,
            uint256,
            uint256
        )
    {
        Project storage p = projects[_projectID];
        return (
            p.admin,
            p.numberOfDonors,
            p.minDonation,
            p.deadline,
            p.goal,
            p.raisedAmount
        );
    }


    function donate(uint256 projectID) public payable {
        Project storage p = projects[projectID];

        //require(block.timestamp < p.deadline, "Deadline has passed!");
        require(msg.value >= p.minDonation, "Minimum Contribution not met!");

        if (p.donors[msg.sender] == 0) {
            p.numberOfDonors++;
        }

        p.donors[msg.sender] += msg.value;

        p.raisedAmount += msg.value;

        emit DonateEvent(projectID, msg.sender, msg.value);
    }


    receive() external payable {}

    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    function getCurrentProjectID() public view returns (uint256) {
        return numProjects;
    }
    
    function getCurrentRequestID() public view returns (uint256) {
        return numberOfRequests;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == sysadm, "Only Admin can call this function!");
        _;
    }

    function createRequest(
        uint256 _projectID,
        string memory _description,
        address payable _recipient,
        uint256 _value
    ) public onlyAdmin returns (uint256 requestID) {
        numberOfRequests = numberOfRequests + 1;
        requestID = numberOfRequests;
        Request storage newRequest = requests[requestID];
    
        newRequest.projectID = _projectID;
        newRequest.description = _description;
        newRequest.recipient = _recipient;
        newRequest.value = _value;
        newRequest.status = "Requested";
        newRequest.numberOfVoters = 0;

        emit CreateRequestEvent(_projectID, _description, _recipient, _value);
    }

    function getRequestInfo(uint256 _requestIndex)
        public
        view
        returns (
            uint256,
            string memory,
            address,
            uint256,
            string memory,
            uint256
        )
    {
        Request storage r = requests[_requestIndex];
        return (
            r.projectID,
            r.description,
            r.recipient,
            r.value,
            r.status,
            r.numberOfVoters
        );
    }

    function voteRequest(uint256 _requestNo) public {
        Request storage r = requests[_requestNo];
        Project storage p = projects[r.projectID];
        require(
            p.donors[msg.sender] > 0,
            "You must be a donor to vote"
        );
        
        require(
            r.voters[msg.sender] == false,
            "You have already voted!"
        );
        r.voters[msg.sender] = true;
        r.numberOfVoters++;
    }

    function makePayment(uint256 _requestNo) public onlyAdmin {
        Request storage r = requests[_requestNo];
        Project storage p = projects[r.projectID];
        require(
            p.raisedAmount >= r.value,
            "You have not raised enough ETH!"
        );
        require(
            keccak256(abi.encodePacked(r.status)) == keccak256(abi.encodePacked("Requested")),
            "The request has been completed!"
        );
        require(r.numberOfVoters > p.numberOfDonors / 2); 

        r.recipient.transfer(r.value);
        r.status = "Completed";

        emit MakePaymentEvent(r.recipient, r.value);
    }
}
