# Avoiding common attacks

## SWC-107 - Re-entrancy

The **cannotBeBusy** modifier is used to ensure the functions donate and make payment can only be executed one at a time. This prevents the reentrancy attack.

## SWC-102 - Outdated Compiler Version

**pragma solidity 0.8.0;** is used in the main contract, which is pretty close to the most recent version.

## SWC-123 - Requirement Violation

The **require()** construct is used to validate external inputs of a function. For example, it is used in MakePayment function to make sure we have enough funding.