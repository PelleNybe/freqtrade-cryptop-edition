import re


with open("freqtrade/rpc/api_server/api_auth.py") as f:
    content = f.read()

# Modify login function
new_login_logic = """
@router_login.post("/token/login", response_model=AccessAndRefreshToken)
async def login_access_token(
    request: Request,
    api_config=Depends(get_api_config),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    \"\"\"OAuth2 compatible token login, get an access token for future requests\"\"\"
    client_ip = request.client.host if request.client else "unknown"

    # Check if locked out
    if login_lockout_cache.get(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account locked due to too many failed login attempts. Please try again in 15 minutes.",
        )

    # Standard rate limit check
    attempts = login_attempts_cache.get(client_ip, 0)
    if attempts >= 5:
        # Lock them out
        login_lockout_cache[client_ip] = True
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Account locked due to too many failed login attempts. Please try again in 15 minutes.",
        )

    if not verify_auth(api_config, form_data.username, form_data.password):
        login_attempts_cache[client_ip] = attempts + 1
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Successful login, reset attempts
    if client_ip in login_attempts_cache:
        del login_attempts_cache[client_ip]
"""

content = re.sub(
    r'@router_login.post\("/token/login",.*?if not verify_auth\(api_config, form_data\.username, form_data\.password\):.*?headers={"WWW-Authenticate": "Bearer"},\n        \)',
    new_login_logic,
    content,
    flags=re.DOTALL,
)


with open("freqtrade/rpc/api_server/api_auth.py", "w") as f:
    f.write(content)
