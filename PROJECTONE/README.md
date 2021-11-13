# ProjectOne
Welcome to ProjectOne! An Ethereum Dapp that allows the donors to help out the underserved communities thru fundraising projects.  It is written in Django, Solidity, Web3.js and Web3.py.

The smart contract is built to accomplish the following functionalities:
1) Allow users with 'Admin' role to create new fundraising projects and funding distribution requests.
2) Allow users with 'Donor' role to donate to the funding projects and vote to the spending requests. 
3) Allow users with 'Admin' role to complete the spending requests if donors have reached consensus.

# ProjectOne Directories
```
PROJECTONE 
> brownie  
    > contracts - location of the smart contract file fundraising.sol
    > tests - location of the test script file test_fundraising.py
> fundraising 
    > contracts - location of the smart contract code fundraising.sol
    > migrations - contains new migrations files based on the changes specified in models.py
    > templates
        > fundraising - contains all UI forms HTML files that belong at the application level.
    urls.py - contains directions for where users should be routed after navigating to a certain URL for fundraising Dapp.
    models.py - defines the structure of stored data that Django has access to.
    utils.py - includes code to deploy the contract and generate ABI and ByteCode and the get functions APIs for the back end.
    views.py - contains a number of different views like pages the user might like to see
> media\projects_imgs: location of the projects uploaded image files
> projectone
    urls.py - contains URL routing information at the project level.
    settings.py - contains setting variables such as blockchain provider, chain_id, my_address, private key and deployed address.
> static
    > css - contains the stylesheet file.
    > images - contains ProjectOne logo and other application related image files.
    > js
        donate.js - front end script to interact with web3.js, donate.html form, MetaMask and the deployed contract.
        vote.js - front end script to interact with web3.js, vote.html form, MetaMask and the deployed contract.
> template: location of the UI forms HTML files that belong at the project level.
    base.html - first level ProjectOne page including ProjectOne logo and nagivation bar items.
```

### Setting up the environment
1) Downloaded the source code from Github.

2) Make sure you have Python installed in your machine.  

3) Change directory to project folder ProjectOne and install all the requirements:

```
pip install -r requirements.txt
```

4) Update fundraising/settings.py and set paramters of web3.py to work with your blockchain provider. If you are working with Ganache be sure to change the following parameters with the ones in your Ganache workspace:

```
provider = "***RPC_server***"
chain_Id = "***network_id***"
```

Change the value of my_address and private_key to set your admin account (I used the first one in my Ganache workspace), from this account will be sent all the transactions for the creation of a new project:

```
my_address = "***admin_address***"
private_key = "***admin_private_key***"
```
5) Start Django local development server:

```
python manage.py makemigrations
python manage.py migrate 
```

Create a superuser as your admin account.

```
python manage.py createsuperuser
```

```
python manage.py runserver
```

6) Start ProjectOne Dapp from a browser session that has MetaMask installed:

```
http://127.0.0.1:8000
```

### Using the platform

1) Create a Project: Use the superuser (admin) account that you created above to login the ProjectOne Dapp, select Create a Project, fill in the form with project image, title, purpose, goal amount in wei, deadline and category then click on the Submit button.

2) Create a Request for a given project: From the admin account, select Find A Project to bring up the project that you just created. Click on the project title to jump to the project detail page. Click on the Requests button to lead you to the Requests main page.  From here you can click on Create Request button to fill in the form with Description, Address To and Value.

3) Make a Donation: Register and login ProjectOne under donor role. Go to project detail page, click on the Donate button to make a contribution.  This form will check if MetaMask is available and allow you to connect to your account.

4) Make a Vote: Use your donor account you can go to the Request detail page (Project detail page -> Requests page -> Request detail page) and click on the Vote button.  This form will check if MetaMask is available and you are required to connect to your account to enable the Yes vote button.

5) Make a Payment: Once the voting consensus is reached meaning once we have numberOfVoters > p.numberOfDonors / 2, the admin account can go to the Request detail page and click on the Make Payment button to distribute fund to the recipient Address To account. 

### Testing with Brownie

To run the tests, from your terminal session under the brownie directory, issue this command:

```
brownie test
```


