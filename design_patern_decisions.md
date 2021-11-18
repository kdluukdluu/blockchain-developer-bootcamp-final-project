# Design Patterns used

## Inheritance and Interfaces

The contract inherits OpenZeppelin's Ownable module. This provides a basic access control mechanism, where there is an account (an owner) that can be granted exclusive access to specific functions. By default, the owner account will be the one that deploys the contract. The module's modifier **onlyOwner** is used to only allow the contract owner to distribute funds from the contract to recipients.

## Access Control Design Patterns

The contract also has a **onlyAdmin** modifier to make sure that only admin can create a project and create a request.