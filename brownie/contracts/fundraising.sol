// contracts/Fundraising.sol
//SPDX-License-Identifier: GPL-3.0

pragma solidity 0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";

/// @title Fundraising Contract to help out the underserved communities
/// @author KDLUU
/// @notice You can use this contract for only the most basic simulation
/// @dev All function calls are currently implemented without side effects
contract Fundraising is Ownable {
    
    // Address of the sysadm
    address public sysadm;
    
    //Struct for storing projects
    //Contains an admin adddress
    //Contains number of donors
    //Contains minimum donation amount in wei
    //Contains a project deadline
    //Contains a project goal amount in wei
    //Contains a raised amount in wei
    //Contains mapping for storing donors' contributions
    struct Project {
        address admin;
        uint256 numberOfDonors;
        uint256 minDonation;
        uint256 deadline; 
        uint256 goal;
        uint256 raisedAmount;
        mapping(address => uint256) donors;
    }
    
    //Stores total number of projects
    uint256 public numProjects;
    
    //Mapping for storing projects
    mapping (uint256 => Project) projects;

    //Struct for storing requests
    //Contains an unique project ID
    //Contains project description
    //Contains an address of recipient
    //Contains a funding request amount in wei
    //Contains a status of the request (Requested or Completed)
    //Contains a total number of voters
    //Contains mapping for storing voters' results
    struct Request {
        uint256 projectID;
        string  description;
        address payable recipient;
        uint256 value;
        string  status;
        uint256 numberOfVoters;
        mapping(address => bool) voters;
    }

    //Contains a total number of requests
    uint256 public numberOfRequests;

    //Contains mapping for storing requests
    mapping(uint256 => Request) public requests;

    /// @notice Determine whether or not a function is completely executed
    /// @dev Used to prevent re-entrancy attacks
    bool public busy = false;
    
    /// @notice Initialize sysadm to msg.sender once the contract is deployed
    constructor() {
        sysadm = msg.sender;
    }
    
    /* Events */
    /// @notice Event emitted when a project is created
    /// @param _projectID a unique project ID
    /// @param _goal Fundraising goal for a given project
    /// @param _deadline Deadline for the fundraising project
    event CreateProjectEvent(uint256 _projectID, uint256 _goal, uint256 _deadline);

    /// @notice Event emitted when a donation is made
    /// @param _projectID Unique ID for the project
    /// @param _sender Donor's address
    /// @param _value Contribution amount
    event DonateEvent(uint256 _projectID, address _sender, uint256 _value);

    /// @notice Event emitted when a funding request is created
    /// @param _projectID a unique project ID
    /// @param _description a description of the funding request
    /// @param _recipient an address of the recipient
    /// @param _value a funding request amount
    event CreateRequestEvent(uint256 _projectID, string _description, address _recipient, uint256 _value);

    /// @notice Event emitted when a payment is made to fullfil the funding request
    /// @param _recipient an address of the recipient
    /// @param _value a funding request amount to go to recipient
    event MakePaymentEvent(address _recipient, uint256 _value);

    /* Modifiers */
    /// @notice Check to make sure only admin can execute the CreateProject, CreateRequest and MakePayment functions
    /// @dev Used to prevent access violation
    modifier onlyAdmin() {
        require(msg.sender == sysadm, "Only Admin can call this function!");
        _;
    }

    /// @notice Check whether some functions did not complete
    /// @dev Used to prevent re-entrancy attacks    
    modifier cannotBeBusy {
        require(!busy, "The previous request is still being processed!");
        busy = true;
        _;
        busy = false;
    }


    /* Functions */
    /// @notice Save new project to array of projects 
    /// @dev Function is onlyAdmin
    /// @dev cannotBeBusy modifier checks whether some functions did not complete; used to prevent re-entrancy attacks
    /// @param _goal The new unencrypted part of the password to be saved
    /// @param _deadline The new encrypted part of the password to be saved
    /// @return projectID once the save operation is executed
    function createProject(uint256 _goal, uint256 _deadline) public onlyAdmin cannotBeBusy returns (uint256 projectID) {
        // Increment to the next project ID
        numProjects = numProjects + 1; 
        projectID = numProjects;

        // Instantiate a new project structure array
        Project storage p = projects[projectID];

        // Then assign a new values to it
        p.goal = _goal;
        p.deadline = block.timestamp + _deadline;
        p.minDonation = 200 wei;
        p.admin = msg.sender;
        
        // Log the event
        emit CreateProjectEvent(projectID, _goal, _deadline);

        // Return a new project ID
        return projectID;
    }

    /// @notice Returns project information for a given project ID 
    /// @dev Function is a public view
    /// @param _projectID a unique project ID
    /// @return admin - an address of the sysadm account
    /// @return numberOfDonors - total number of donors
    /// @return minDonation - minimum donation amount
    /// @return deadLine - project deadline
    /// @return goal - project goal in wei
    /// @return raisedAmount - total raised amount in wei
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

    /// @notice Add donation amount to the storage array of project donors and update raised amount
    /// @dev Function is a payable
    /// @dev cannotBeBusy modifier checks whether some functions did not complete; used to prevent re-entrancy attacks
    /// @dev donation value in wei must be greater or equal to the minimum donation amount.
    /// @param _projectID a unique project ID
    /// @return true if the donate function successfully executed
    function donate(uint256 _projectID) public payable cannotBeBusy returns (bool) {
        Project storage p = projects[_projectID];

        require(msg.value >= p.minDonation, "Minimum Donation not met!");

        if (p.donors[msg.sender] == 0) {
            p.numberOfDonors++;
        }

        p.donors[msg.sender] += msg.value;

        p.raisedAmount += msg.value;

        emit DonateEvent(_projectID, msg.sender, msg.value);

        return true;
    }

    /// @dev The receive method is used as a fallback function in a contract and is called when ether is sent to a contract with no calldata.
    receive() external payable {}

    /// @notice Returns a balance from a current address
    /// @dev Function is a public view
    /// @return a balance from a current account
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }

    /// @notice Returns a current project ID
    /// @dev Function is a public view
    /// @return a current project ID
    function getCurrentProjectID() public view returns (uint256) {
        return numProjects;
    }
    
    /// @notice Returns a current request ID
    /// @dev Function is a public view
    /// @return a current request ID
    function getCurrentRequestID() public view returns (uint256) {
        return numberOfRequests;
    }

    /// @notice Add new funding request to the storage arry of requests.
    /// @dev onlyAdmin modifier checks to make sure only admin can execute this function.
    /// @param _projectID a unique project ID
    /// @param _description funding request description
    /// @param _recipient an address of the recipient
    /// @param _value an amount funding request in wei
    /// @return requestID if the function successfully executed
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

        return requestID;
    }

    /// @notice Return the request information for a given request ID.
    /// @param _requestIndex a unique request ID
    /// @return projectID an unique project ID
    /// @return description a request description
    /// @return recipient an adddress of the recipient
    /// @return value an funding request amount in wei
    /// @return status a status of the request that can be Requested or Completed
    /// @return numberOfVoters a current number of voters
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

    /// @notice Record the voter result in the storage array of voters for a given request ID
    /// @dev Check to make sure user must be a donor in order to vote.
    /// @dev Check to make sure you can only vote once.
    /// @param _requestNo a unique request ID
    /// @return true if the function successfully executed
    function voteRequest(uint256 _requestNo) public returns (bool) {
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

        return true;
    }

    /// @notice Transfer funding to the recipient address for a given request ID
    /// @dev onlyAdmin modifier check to ensure that only admin can execute this function
    /// @dev cannotBeBusy modifier checks whether some functions did not complete; used to prevent re-entrancy attacks
    /// @dev check to ensure that the raised amount must be greater or equal to the distribution amount request
    /// @dev check to ensure that the request is not completed yet
    /// @dev check to ensure that the consensus is reached among the voters
    /// @param _requestNo a unique request ID
    /// @return true if the donate function successfully executed
    function makePayment(uint256 _requestNo) public onlyOwner cannotBeBusy returns (bool) {
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

        return true;
    }
}
