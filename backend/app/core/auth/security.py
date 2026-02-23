"""
Security Utilities: JWT Tokens & Password Hashing

HOW AUTH WORKS (THE BIG PICTURE):
================================

    1.  REGISTER:
        User sends email + password
        -> We hash the password with bcrypt
        -> Store email + hash in database
    
    2.  Login:
        User sends email + password
        -> We find the user by email
        -> We verify password against stored hash
        -> If correct, we create a JWT token and return it

    3.  AUTHENTICATED REQUESTS:
        User sends request with JWT in Authorization header
        -> We decode the JWT to get the user_id
        -> We look up the user in the database
        -> If valid, we allow the request

WHY JWT (JSON Web Tokens)?
==========================
- Stateless: The server doesn't need to store sessions
- Scalable: Works with multiple server instances
- Self-contained: The token carries the user's identity
Industry standard: Used by most modern APIs        

A JWT looks like: xxxxx.yyyyy.zzzzz (three parts)
- Header: Algorithm used
- Payload: Data (user_id, experation time, etc)
- Signature: Proves the token wasn't tampered with        
"""