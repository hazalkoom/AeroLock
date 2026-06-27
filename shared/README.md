# AeroLock Shared Package (`aerolock-common`)

This is a local Python package that contains code shared across the Gateway, Inventory, and Search services.

## What it does

Instead of duplicating code in every service, common utilities and definitions are centralized here:
*   **Protocol Buffers (Protobufs)**: The `.proto` files defining the gRPC interfaces and message structures between the services.
*   **Configuration**: Shared Pydantic settings and environment variable parsers.
*   **Errors**: Common exception classes and error handling utilities.

## Structure
*   `aerolock_common/`: The actual Python module containing the shared code.
    *   `grpc/`: The generated Python code from the protobuf definitions.
    *   `config/`: Shared configurations.

## Development

This package is installed in the other services using Poetry path dependencies (`aerolock-common = {path = "../shared", develop = false}`).

If you modify the protobuf definitions, you must re-generate the Python gRPC code. (See Makefile in the project root).
